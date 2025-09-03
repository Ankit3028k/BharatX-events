const express = require('express');
const bodyParser = require('body-parser');
const nodemailer = require('nodemailer');
const app = express();
const port = 3000;

app.use((req, res, next) => {
  const allowedOrigins = ['http://127.0.0.1:5500', 'http://localhost:5500'];
  const origin = req.headers.origin;
  if (allowedOrigins.includes(origin)) {
       res.setHeader('Access-Control-Allow-Origin', origin);
  }
  res.header('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, X-Requested-With');
  if (req.method === 'OPTIONS') {
    res.sendStatus(200);
  } else {
    next();
  }
});
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

app.post('/forms/contact', (req, res) => {
    const { name, email, subject, message } = req.body;

    const transporter = nodemailer.createTransport({
        host: 'smtp.gmail.com',
        port: 465,
        secure: true,
        auth: {
            user: 'ankitgangrade9617@gmail.com',
            pass: 'jvllhzynauypzmmx'
        }
    });

    const mailOptions = {
        from: `"${name}" <${email}>`,
        to: 'ankitgangrade8959@gmail.com',
        subject: subject,
        text: message
    };

    transporter.sendMail(mailOptions, (error, info) => {
        if (error) {
            return res.status(500).send(error.toString());
        }
        res.status(200).send('OK');
    });
});

app.post('/forms/buy-tickets', (req, res) => {
    const { first_name, last_name, email, phone, company, job_title, quantity, dietary, special_requests } = req.body;

    const transporter = nodemailer.createTransport({
        host: 'smtp.gmail.com',
        port: 465,
        secure: true,
        auth: {
            user: 'ankitgangrade9617@gmail.com',
            pass: 'jvllhzynauypzmmx'
        }
    });

    const mailOptions = {
        from: `"${first_name} ${last_name}" <${email}>`,
        to: 'ankitgangrade8959@gmail.com',
        subject: 'New Ticket Purchase',
        html: `
            <p><strong>Name:</strong> ${first_name} ${last_name}</p>
            <p><strong>Email:</strong> ${email}</p>
            <p><strong>Phone:</strong> ${phone}</p>
            <p><strong>Company:</strong> ${company}</p>
            <p><strong>Job Title:</strong> ${job_title}</p>
            <p><strong>Quantity:</strong> ${quantity}</p>
            <p><strong>Dietary Restrictions:</strong> ${dietary}</p>
            <p><strong>Special Requests:</strong> ${special_requests}</p>
        `
    };

    transporter.sendMail(mailOptions, (error, info) => {
        if (error) {
            return res.status(500).send(error.toString());
        }
        res.status(200).send('Ticket request sent successfully');
    });
});

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});