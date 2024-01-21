const express = require('express');
const path = require('path');
const app = express();

const PORT = process.env.PORT || 3000;

// Serve static files from the 'public' folder
app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public/index.html'));
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});


// const db = new sqlite3.Database('mydatabase.db', (err) => {
//     if (err) {
//         console.error(err.message);
//     }
//     console.log('Connected to the SQLite database.');

//     db.run(`CREATE TABLE IF NOT EXISTS users (
//         email TEXT PRIMARY KEY
//     )`);

//     db.run(`CREATE TABLE IF NOT EXISTS locations (
//         location_id INTEGER PRIMARY KEY AUTOINCREMENT,
//         user_email TEXT,
//         start TEXT,
//         end TEXT,
//         distance REAL,
//         time TEXT,
//         FOREIGN KEY (user_email) REFERENCES users (email)
//     )`);
// });
