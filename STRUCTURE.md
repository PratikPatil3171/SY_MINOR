# Project Structure Documentation

## 📁 Organized File Structure

```
Personalized/
│
├── 📂 public/                      # All frontend files (HTML, CSS, JS, Images)
│   ├── 📂 css/
│   │   └── main.css               # ✅ Renamed from styles.css
│   │
│   ├── 📂 js/
│   │   └── app.js                 # ✅ Frontend logic
│   │
│   ├── 📂 images/                 # ✅ All image assets
│   │   ├── Gemini_Generated_Image_lco3ualco3ualco3.png
│   │   ├── hero-illustration.svg
│   │   ├── Pratik Photo.jpeg
│   │   └── WhatsApp Image 2025-12-02 at 16.14.31_3f5393ef.jpg
│   │
│   └── index.html                 # ✅ Main HTML file
│
├── 📂 src/                         # Backend source code
│   ├── server.js                  # ✅ Express server (moved from root)
│   └── config.js                  # ✅ Configuration settings (new)
│
├── 📂 data/                        # Database files
│   └── database.json              # ✅ Renamed from db.json
│
├── 📂 tests/                       # Testing files
│   └── api-test-client.html       # ✅ Renamed from test_client.html
│
├── 📂 node_modules/                # Dependencies (auto-generated)
│
├── .gitignore                     # ✅ Git ignore file (new)
├── package.json                   # ✅ Updated with new paths
├── package-lock.json              # Auto-generated
└── README.md                      # ✅ Updated documentation
```

## 🎯 Changes Made

### File Reorganization
| Old Location | New Location | Status |
|-------------|--------------|--------|
| `styles.css` | `public/css/main.css` | ✅ Moved & Renamed |
| `app.js` | `public/js/app.js` | ✅ Moved |
| `index.html` | `public/index.html` | ✅ Moved |
| `server.js` | `src/server.js` | ✅ Moved |
| `db.json` | `data/database.json` | ✅ Moved & Renamed |
| `test_client.html` | `tests/api-test-client.html` | ✅ Moved & Renamed |
| All images | `public/images/` | ✅ Moved |

### New Files Created
- ✅ `src/config.js` - Centralized configuration
- ✅ `.gitignore` - Git ignore rules
- ✅ `STRUCTURE.md` - This documentation file

### Updated Files
- ✅ `public/index.html` - Updated CSS/JS paths
- ✅ `src/server.js` - Updated database and static paths
- ✅ `package.json` - Updated main entry point
- ✅ `README.md` - Updated project structure section

## 📋 Naming Conventions Applied

### ✅ Files
- Use **lowercase** with **hyphens** for multi-word files: `api-test-client.html`
- Use **descriptive names**: `main.css` instead of `styles.css`
- Use **clear prefixes**: `database.json` instead of `db.json`

### ✅ Folders
- Use **lowercase** without special characters
- Use **plural names** for collections: `images`, `tests`
- Use **clear purpose**: `public` (frontend), `src` (backend), `data` (storage)

## 🎨 Benefits of This Structure

1. **Separation of Concerns**: Frontend (public) and Backend (src) are clearly separated
2. **Scalability**: Easy to add more modules, routes, or features
3. **Maintainability**: Developers can quickly find files
4. **Professional**: Follows industry-standard conventions
5. **Security**: Sensitive files can be easily protected (data/, .env)

## 🚀 Running the Application

```bash
# Start the server
npm start

# Server runs at: http://localhost:3000
```

All paths have been updated automatically. The application works seamlessly with the new structure!
