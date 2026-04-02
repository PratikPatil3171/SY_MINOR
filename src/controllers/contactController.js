const nodemailer = require('nodemailer');

const CONTACT_RECEIVER_EMAIL = process.env.CONTACT_RECEIVER_EMAIL || 'careerpathsupport@gmail.com';

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(email || '').trim());
}

function buildTransport() {
  const host = process.env.SMTP_HOST || 'smtp.gmail.com';
  const port = Number(process.env.SMTP_PORT || 587);
  const secure = String(process.env.SMTP_SECURE || 'false').toLowerCase() === 'true';
  const user = process.env.SMTP_USER;
  const pass = process.env.SMTP_PASS;

  if (!user || !pass) {
    throw new Error('SMTP credentials are not configured. Set SMTP_USER and SMTP_PASS in .env');
  }

  if (String(user).includes('your_sender_email')) {
    throw new Error('SMTP_USER is still a placeholder. Set your real Gmail address in .env');
  }

  if (String(pass).toLowerCase().includes('app_password') || String(pass).toLowerCase().includes('your_')) {
    throw new Error('SMTP_PASS is still a placeholder. Set a real Gmail App Password in .env');
  }

  return nodemailer.createTransport({
    host,
    port,
    secure,
    auth: {
      user,
      pass,
    },
  });
}

exports.sendContactQuery = async (req, res) => {
  try {
    const name = String(req.body?.name || '').trim();
    const email = String(req.body?.email || '').trim();
    const message = String(req.body?.message || '').trim();

    if (!name || !email || !message) {
      return res.status(400).json({
        ok: false,
        message: 'Name, email, and query are required.',
      });
    }

    if (!isValidEmail(email)) {
      return res.status(400).json({
        ok: false,
        message: 'Please provide a valid email address.',
      });
    }

    const transporter = buildTransport();
    const fromAddress = process.env.MAIL_FROM || process.env.SMTP_USER;

    const mail = {
      from: `CareerPath Contact Form <${fromAddress}>`,
      to: CONTACT_RECEIVER_EMAIL,
      replyTo: email,
      subject: `New Contact Query from ${name}`,
      text: [
        'New query submitted from CareerPath Contact Us form.',
        '',
        `Name: ${name}`,
        `Email: ${email}`,
        '',
        'Query:',
        message,
      ].join('\n'),
      html: `
        <h3>New Contact Query</h3>
        <p><strong>Name:</strong> ${name}</p>
        <p><strong>Email:</strong> ${email}</p>
        <p><strong>Query:</strong></p>
        <p>${message.replace(/\n/g, '<br/>')}</p>
      `,
    };

    await transporter.verify();
    await transporter.sendMail(mail);

    return res.status(200).json({
      ok: true,
      message: 'Your query has been sent successfully.',
    });
  } catch (error) {
    console.error('Contact query email failed:', error.message);

    const errText = String(error && error.message ? error.message : '').toLowerCase();
    if (errText.includes('invalid login') || errText.includes('badcredentials') || errText.includes('535-5.7.8')) {
      return res.status(500).json({
        ok: false,
        message: 'SMTP login failed. Please set correct SMTP_USER and Gmail App Password (SMTP_PASS) in .env.',
      });
    }

    if (errText.includes('placeholder')) {
      return res.status(500).json({
        ok: false,
        message: error.message,
      });
    }

    return res.status(500).json({
      ok: false,
      message: 'Unable to send your query right now. Please try again later.',
    });
  }
};
