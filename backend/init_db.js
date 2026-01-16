const mysql = require('mysql2/promise');
const fs = require('fs');
const path = require('path');

const DB_CONFIG = {
    host: '127.0.0.1',
    user: 'root',
    password: '1q2w3e4r',
    rowsAsRows: false,
    multipleStatements: true 
};

const DB_NAME = 'mood_diary';

async function initDb() {
    let connection;
    try {
        console.log(`Connecting to MariaDB at ${DB_CONFIG.host}...`);
        connection = await mysql.createConnection(DB_CONFIG);

        // 1. Create Database
        console.log(`Creating database '${DB_NAME}' if not exists...`);
        await connection.query(`CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`);

        // 2. Use Database
        console.log(`Using database '${DB_NAME}'...`);
        await connection.query(`USE ${DB_NAME};`);

        // 3. Read schema.sql
        const schemaPath = path.join(__dirname, 'schema.sql');
        console.log(`Reading schema from ${schemaPath}...`);
        const schemaSql = fs.readFileSync(schemaPath, 'utf8');

        // 4. Execute Schema
        // Note: multipleStatements=true allows executing the whole file if it contains multiple queries
        console.log('Executing schema...');
        await connection.query(schemaSql);
        
        console.log('Schema applied successfully!');

        // 5. Verify
        const [rows] = await connection.query('SHOW TABLES;');
        console.log(`Current tables in ${DB_NAME}:`);
        rows.forEach(row => {
            // The key for the table name depends on the column name returned by SHOW TABLES
            // usually "Tables_in_dbname"
            const tableName = Object.values(row)[0];
            console.log(` - ${tableName}`);
        });

    } catch (err) {
        console.error('An error occurred:', err);
    } finally {
        if (connection) {
            await connection.end();
            console.log('Connection closed.');
        }
    }
}

initDb();
