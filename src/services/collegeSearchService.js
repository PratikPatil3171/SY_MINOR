const fs = require('fs');
const path = require('path');
const XLSX = require('xlsx');

const DATA_DIR = path.join(__dirname, '..', '..', 'data');
const SUPPORTED_FILES = [
  'Maharashtra_Engineering_Colleges_Complete_Final.xlsx',
  'engineering_colleges.xlsx',
  'engineering_colleges.json',
  'engineering_colleges.csv',
  'maharashtra_engineering_colleges.csv',
  'colleges.csv',
];

const CACHE_TTL_MS = 5 * 60 * 1000;

let cache = {
  loadedAt: 0,
  records: [],
};

function normalizeText(value) {
  return String(value || '').trim();
}

function normalizeKey(value) {
  return normalizeText(value).toLowerCase().replace(/[^a-z]/g, '');
}

function csvLineToArray(line) {
  const result = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < line.length; i += 1) {
    const ch = line[i];

    if (ch === '"') {
      const next = line[i + 1];
      if (inQuotes && next === '"') {
        current += '"';
        i += 1;
      } else {
        inQuotes = !inQuotes;
      }
      continue;
    }

    if (ch === ',' && !inQuotes) {
      result.push(current);
      current = '';
      continue;
    }

    current += ch;
  }

  result.push(current);
  return result.map((item) => item.trim());
}

function findHeaderIndex(headers, aliases) {
  const normalizedHeaders = headers.map((header) => normalizeKey(header));
  for (const alias of aliases) {
    const idx = normalizedHeaders.indexOf(normalizeKey(alias));
    if (idx !== -1) return idx;
  }
  return -1;
}

function toCollegeRow(input) {
  if (!input || typeof input !== 'object') return null;

  const keyMap = {};
  Object.keys(input).forEach((key) => {
    keyMap[normalizeKey(key)] = input[key];
  });

  const district = normalizeText(
    keyMap.district || keyMap.districtname || keyMap.city || keyMap.region
  );
  const collegeName = normalizeText(
    keyMap.collegename || keyMap.college || keyMap.institute || keyMap.institutename
  );
  const branch = normalizeText(
    keyMap.branch || keyMap.branchname || keyMap.course || keyMap.department
  );
  const websiteUrl = normalizeText(
    keyMap.officialwebsitelink ||
      keyMap.officialwebsite ||
      keyMap.website ||
      keyMap.websiteurl ||
      keyMap.weblink ||
      keyMap.url
  );

  if (!district || !collegeName || !branch) {
    return null;
  }

  return {
    district,
    collegeName,
    branch,
    websiteUrl,
  };
}

function parseCsv(fileContent) {
  const lines = fileContent
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);

  if (lines.length < 2) return [];

  const headers = csvLineToArray(lines[0]);
  const districtIdx = findHeaderIndex(headers, ['district', 'district name', 'city']);
  const collegeIdx = findHeaderIndex(headers, ['college name', 'college', 'institute']);
  const branchIdx = findHeaderIndex(headers, ['branch', 'branch name', 'course', 'department']);
  const websiteIdx = findHeaderIndex(headers, ['official website link', 'website', 'web link', 'url']);

  if (districtIdx === -1 || collegeIdx === -1 || branchIdx === -1) {
    return [];
  }

  const output = [];

  for (let i = 1; i < lines.length; i += 1) {
    const cols = csvLineToArray(lines[i]);
    const row = {
      district: cols[districtIdx] || '',
      collegeName: cols[collegeIdx] || '',
      branch: cols[branchIdx] || '',
      websiteUrl: websiteIdx === -1 ? '' : cols[websiteIdx] || '',
    };

    const normalized = toCollegeRow(row);
    if (normalized) output.push(normalized);
  }

  return output;
}

function listCandidateDataFiles() {
  const preferred = SUPPORTED_FILES
    .map((fileName) => path.join(DATA_DIR, fileName))
    .filter((absolutePath) => fs.existsSync(absolutePath));

  let discovered = [];
  try {
    discovered = fs
      .readdirSync(DATA_DIR)
      .filter((name) => /\.(xlsx|xls|csv|json)$/i.test(name))
      .map((name) => path.join(DATA_DIR, name));
  } catch (error) {
    discovered = [];
  }

  const ordered = Array.from(new Set([...preferred, ...discovered]));

  return ordered.sort((left, right) => {
    const leftExt = path.extname(left).toLowerCase();
    const rightExt = path.extname(right).toLowerCase();

    const leftIsWorkbook = leftExt === '.xlsx' || leftExt === '.xls';
    const rightIsWorkbook = rightExt === '.xlsx' || rightExt === '.xls';

    if (leftIsWorkbook && !rightIsWorkbook) return -1;
    if (!leftIsWorkbook && rightIsWorkbook) return 1;

    return left.localeCompare(right);
  });
}

function parseCollegeRowsFromFile(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  const isExcel = ext === '.xlsx' || ext === '.xls';
  const content = isExcel ? '' : fs.readFileSync(filePath, 'utf8');

  if (isExcel) {
    const workbook = XLSX.readFile(filePath);
    const firstSheetName = workbook.SheetNames[0];
    if (!firstSheetName) return [];

    const worksheet = workbook.Sheets[firstSheetName];
    const rows = XLSX.utils.sheet_to_json(worksheet, { defval: '' });
    return rows.map(toCollegeRow).filter(Boolean);
  }

  if (ext === '.json') {
    const parsed = JSON.parse(content);
    const rawArray = Array.isArray(parsed)
      ? parsed
      : Array.isArray(parsed.colleges)
      ? parsed.colleges
      : [];

    return rawArray.map(toCollegeRow).filter(Boolean);
  }

  if (ext === '.csv') {
    return parseCsv(content);
  }

  return [];
}

function loadRawRows() {
  const candidateFiles = listCandidateDataFiles();
  const mergedRows = [];

  for (const filePath of candidateFiles) {
    try {
      const rows = parseCollegeRowsFromFile(filePath);
      if (rows.length > 0) {
        mergedRows.push(...rows);
      }
    } catch (error) {
      // Ignore non-college files and keep searching for a valid dataset.
    }
  }

  return mergedRows;
}

function aggregateByCollege(rows) {
  const grouped = new Map();

  rows.forEach((row) => {
    const id = `${row.district.toLowerCase()}::${row.collegeName.toLowerCase()}`;

    if (!grouped.has(id)) {
      grouped.set(id, {
        district: row.district,
        collegeName: row.collegeName,
        branches: new Set(),
        websiteUrl: row.websiteUrl || '',
      });
    }

    const current = grouped.get(id);
    if (row.branch) current.branches.add(row.branch);
    if (!current.websiteUrl && row.websiteUrl) current.websiteUrl = row.websiteUrl;
  });

  return Array.from(grouped.values()).map((item) => ({
    district: item.district,
    collegeName: item.collegeName,
    branches: Array.from(item.branches).sort((a, b) => a.localeCompare(b)),
    branchCount: item.branches.size,
    websiteUrl: item.websiteUrl,
  }));
}

function getAllColleges() {
  const now = Date.now();
  if (now - cache.loadedAt < CACHE_TTL_MS && cache.records.length > 0) {
    return cache.records;
  }

  const rows = loadRawRows();
  const records = aggregateByCollege(rows);

  cache = {
    loadedAt: now,
    records,
  };

  return records;
}

function toSetFromCsv(input) {
  if (!input) return new Set();
  if (Array.isArray(input)) {
    return new Set(input.map((val) => normalizeText(val).toLowerCase()).filter(Boolean));
  }
  return new Set(
    String(input)
      .split(',')
      .map((part) => part.trim().toLowerCase())
      .filter(Boolean)
  );
}

function scoreCollege(college, query) {
  if (!query) return 0;

  const q = query.toLowerCase();
  const name = college.collegeName.toLowerCase();
  const district = college.district.toLowerCase();
  const branchHits = college.branches.filter((branch) => branch.toLowerCase().includes(q)).length;

  let score = 0;

  if (name === q) score += 120;
  if (name.startsWith(q)) score += 80;
  if (name.includes(q)) score += 50;

  if (district === q) score += 40;
  if (district.includes(q)) score += 25;

  if (branchHits > 0) score += 25 + branchHits * 10;

  return score;
}

function matchesBranchFilter(college, branchFilters) {
  if (branchFilters.size === 0) return true;

  return college.branches.some((branch) => {
    const normalizedBranch = branch.toLowerCase();
    for (const selected of branchFilters) {
      if (normalizedBranch.includes(selected)) return true;
    }
    return false;
  });
}

function buildFacets(records) {
  const districtCounts = new Map();
  const branchCounts = new Map();

  records.forEach((item) => {
    districtCounts.set(item.district, (districtCounts.get(item.district) || 0) + 1);
    item.branches.forEach((branch) => {
      branchCounts.set(branch, (branchCounts.get(branch) || 0) + 1);
    });
  });

  const districts = Array.from(districtCounts.entries())
    .map(([value, count]) => ({ value, count }))
    .sort((a, b) => a.value.localeCompare(b.value));

  const branches = Array.from(branchCounts.entries())
    .map(([value, count]) => ({ value, count }))
    .sort((a, b) => b.count - a.count || a.value.localeCompare(b.value));

  return { districts, branches };
}

function searchColleges(params = {}) {
  const all = getAllColleges();

  const query = normalizeText(params.q).toLowerCase();
  const districtFilters = toSetFromCsv(params.districts);
  const branchFilters = toSetFromCsv(params.branches);
  const hasWebsiteRaw = normalizeText(params.hasWebsite).toLowerCase();

  const page = Math.max(1, Number.parseInt(params.page, 10) || 1);
  const limit = Math.min(5000, Math.max(1, Number.parseInt(params.limit, 10) || 1000));
  const sort = normalizeText(params.sort || 'relevance').toLowerCase();

  const filtered = all
    .map((college) => ({
      ...college,
      relevanceScore: scoreCollege(college, query),
    }))
    .filter((college) => {
      if (query) {
        const inName = college.collegeName.toLowerCase().includes(query);
        const inDistrict = college.district.toLowerCase().includes(query);
        const inBranch = college.branches.some((branch) => branch.toLowerCase().includes(query));
        if (!inName && !inDistrict && !inBranch) return false;
      }

      if (districtFilters.size > 0 && !districtFilters.has(college.district.toLowerCase())) {
        return false;
      }

      if (!matchesBranchFilter(college, branchFilters)) {
        return false;
      }

      if (hasWebsiteRaw === 'true' && !college.websiteUrl) {
        return false;
      }

      if (hasWebsiteRaw === 'false' && !!college.websiteUrl) {
        return false;
      }

      return true;
    });

  const facets = buildFacets(filtered);

  const sorted = [...filtered].sort((a, b) => {
    if (sort === 'name') {
      return a.collegeName.localeCompare(b.collegeName);
    }

    if (sort === 'district') {
      return a.district.localeCompare(b.district) || a.collegeName.localeCompare(b.collegeName);
    }

    if (b.relevanceScore !== a.relevanceScore) {
      return b.relevanceScore - a.relevanceScore;
    }

    return a.collegeName.localeCompare(b.collegeName);
  });

  const totalCount = sorted.length;
  const totalPages = Math.max(1, Math.ceil(totalCount / limit));
  const start = (page - 1) * limit;

  return {
    results: sorted.slice(start, start + limit),
    totalCount,
    page,
    limit,
    totalPages,
    facets,
    sourceCount: all.length,
  };
}

module.exports = {
  searchColleges,
};
