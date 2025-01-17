const express = require('express');
const mysql = require('mysql2');
const cors = require('cors'); // 引入 cors 包
const bodyParser = require('body-parser');
const axios = require('axios');
const cheerio = require('cheerio');



const app = express();
app.use(bodyParser.json());
const port = 3000;

app.use(cors()); // 启用 CORS 中间件

const connection = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: '10214304412',
    database: 'aqi_db'
});

connection.connect(err => {
    if (err) {
        console.error('Error connecting to the database:', err);
        return;
    }
    console.log('Connected to the MySQL server.');

    // // Create aqi_user table if not exists
    // const createTableQuery = `
    //     CREATE TABLE IF NOT EXISTS aqi_user (
    //         id INT AUTO_INCREMENT PRIMARY KEY,
    //         username VARCHAR(255) NOT NULL UNIQUE,
    //         password VARCHAR(255) NOT NULL,
    //         email VARCHAR(255) NOT NULL UNIQUE
    //     )
    // `;
    // connection.query(createTableQuery, (err, result) => {
    //     if (err) throw err;
    //     console.log('aqi_user table created or already exists');
    // });

});


const cityNameMapping = {
    '北京': 'beijing',
    '天津': 'tianjin',
    '上海': 'shanghai',
    '重庆': 'chongqing',
    '石家庄': 'shijiazhuang',
    '太原': 'taiyuan',
    '西安': 'xian',
    '济南': 'jinan',
    '郑州': 'zhengzhou',
    '沈阳': 'shenyang',
    '长春': 'changchun',
    '哈尔滨': 'harbin',
    '南京': 'nanjing',
    '杭州': 'hangzhou',
    '合肥': 'hefei',
    '南昌': 'nanchang',
    '福州': 'fuzhou',
    '武汉': 'wuhan',
    '长沙': 'changsha',
    '成都': 'chengdu',
    '贵阳': 'guiyang',
    '昆明': 'kunming',
    '广州': 'guangzhou',
    '海口': 'haikou',
    '兰州': 'lanzhou',
    '西宁': 'xining',
    '呼和浩特': 'huhehaote',
    '乌鲁木齐': 'wulumuqi',
    '拉萨': 'lhasa',
    '南宁': 'nanning',
    '银川': 'yinchuan'
};

const cityEnNameMapping = {
    'beijing': '北京',
    'tianjin': '天津',
    'shanghai': '上海',
    'chongqing': '重庆',
    'shijiazhuang': '石家庄',
    'taiyuan': '太原',
    'xian': '西安',
    'jinan': '济南',
    'zhengzhou': '郑州',
    'shenyang': '沈阳',
    'changchun': '长春',
    'harbin': '哈尔滨',
    'nanjing': '南京',
    'hangzhou': '杭州',
    'hefei': '合肥',
    'nanchang': '南昌',
    'fuzhou': '福州',
    'wuhan': '武汉',
    'changsha': '长沙',
    'chengdu': '成都',
    'guiyang': '贵阳',
    'kunming': '昆明',
    'guangzhou': '广州',
    'haikou': '海口',
    'lanzhou': '兰州',
    'xining': '西宁',
    'huhehaote': '呼和浩特',
    'wulumuqi': '乌鲁木齐',
    'lhasa': '拉萨',
    'nanning': '南宁',
    'yinchuan': '银川',
    'hongkong': '香港',
    'macau': '澳门',
    'taibei': '台北'
};


const cityEnName = Object.keys(cityEnNameMapping);


async function fetchData(url, city_en) {
    try {
        const response = await axios.get(url);
        const $ = cheerio.load(response.data);

        const result = {};

        // 提取所需的信息
        const aqi = $('#aqiwgtvalue').text().trim();
        const temp = $('#cur_t').text().trim();
        const pm25 = $('#cur_pm25').text().trim();
        const humidity = $('#cur_h').text().trim();
        const wind = $('#cur_w').text().trim();

        result['城市'] = cityEnNameMapping[city_en];
        result['AQI'] = aqi;
        result['PM25'] = pm25;
        result['temperature'] = temp;
        result['wind'] = wind;
        result['humidity'] = humidity;

        console.log(result)

        return result;
    } catch (error) {
        console.error('Error fetching data:', error);
        return null;
    }
}
  


// 用户注册
app.post('/register', (req, res) => {
    const { username, password, email } = req.body;
    const insertQuery = 'INSERT INTO aqi_user (username, password, email) VALUES (?, ?, ?)';
    connection.query(insertQuery, [username, password, email], (err, result) => {
        if (err) {
            if (err.code === 'ER_DUP_ENTRY') {
                res.json({'success_flag':false, 'message':'用户已存在，请重试!'});
            } else {
                res.json({'success_flag':false, 'message':'用户信息错误!'});
            }
        } else {
            res.json({'success_flag':true, 'message':'注册成功!'});
        }
    });
});

// 用户登录
app.post('/login', (req, res) => {
    const { username, password } = req.body;
    const selectQuery = 'SELECT * FROM aqi_user WHERE username = ? AND password = ?';
    connection.query(selectQuery, [username, password], (err, results) => {
        if (err) {
            res.json({'success_flag':false, 'message':'登录错误，请重试!'});
        } else {
            if (results.length > 0) {
                res.json({'success_flag':true, 'message':'登录成功!'});
            } else {
                res.json({'success_flag':false, 'message':'无效的用户名或密码!'});
            }
        }
    });
});

app.get('/city/:cityName', (req, res) => {
    const cityName = req.params.cityName;
    const tableName = cityNameMapping[cityName];

    if (!tableName) {
        return res.status(404).json({ error: 'City not found' });
    }

    const query = `SELECT * FROM ${tableName}`;
    connection.query(query, (err, results) => {
        if (err) {
            console.error('Error executing query:', err);
            return res.status(500).json({ error: 'Database error' });
        }

        res.json(results);
    });
});

app.get('/aqi_data_year', (req, res) => {
    const tableName = 'aqi_data_year'

    const query = `SELECT * FROM ${tableName}`;
    connection.query(query, (err, results) => {
        if (err) {
            console.error('Error executing query:', err);
            return res.status(500).json({ error: 'Database error' });
        }

        res.json(results);
    });
});


app.get('/fetch_cur_aqi', async (req, res) => {
    const currentDate = new Date().toISOString().split('T')[0].replace(/-/g, '');
    const tableName = `aqi_data_${currentDate}`;

    console.log(tableName)

    connection.query(`SHOW TABLES LIKE '${tableName}'`, async (error, results) => {
        if (error) {
            console.error('Error checking table:', error);
            res.status(500).json({ error: 'Internal Server Error' });
            return;
        }

        if (results.length > 0) {
            // 查询数据库，如果有实时数据库则无需爬取
            connection.query(`SELECT * FROM ${tableName}`, (error, results) => {
                if (error) {
                    console.error('Error fetching data from table:', error);
                    res.status(500).json({ error: 'Internal Server Error' });
                    return;
                }
                console.log(results);
                res.json(results);
            });
        } else {
             // 如果没有实时数据则进行爬取
            let cur_aqi_data = [];

            try {
                for (let i = 0; i < cityEnName.length; i++) {
                    console.log(i);
                    let city = cityEnName[i];
                    let fetch_url = 'https://aqicn.org/city/' + city + '/';
                    if (city == 'harbin')
                        fetch_url = 'https://aqicn.org/city/china/haerbin/xiangfanghongqidajie/';
                    if (city == 'xining')
                        fetch_url = 'https://aqicn.org/city/china/xining/chengbeiquzhengfu/';
                    if (city == 'hongkong')
                        fetch_url = 'https://aqicn.org/city/hongkong/central/';
                    if (city == 'macau')
                        fetch_url = 'https://aqicn.org/city/macau/ka-ho/';
                    if (city == 'taibei')
                        fetch_url = 'https://aqicn.org/city/taiwan/jhongshan/';

                    let data = await fetchData(fetch_url, city);
                    cur_aqi_data.push(data);
                }

                console.log(cur_aqi_data);

                // 把爬取的数据存入数据中
                connection.query(`CREATE TABLE ${tableName} (id INT AUTO_INCREMENT PRIMARY KEY, city VARCHAR(255), AQI VARCHAR(255), PM25 VARCHAR(255), temperature VARCHAR(255), wind VARCHAR(255), humidity VARCHAR(255))`, (error) => {
                    if (error) {
                        console.error('Error creating table:', error);
                        res.status(500).json({ error: 'Internal Server Error' });
                        return;
                    }

                    cur_aqi_data.forEach(data => {
                        connection.query(`INSERT INTO ${tableName} (city, AQI, PM25, temperature, wind, humidity) VALUES (?, ?, ?, ?, ?, ?)`, [data['城市'], data['AQI'], data['PM25'], data['temperature'], data['wind'], data['humidity']], (error) => {
                            if (error) {
                                console.error('Error inserting data:', error);
                            }
                        });
                    });

                    res.json(cur_aqi_data);
                });
            } catch (error) {
                console.error('Error fetching data:', error);
                res.status(500).json({ error: 'Internal Server Error' });
            }
        }
    });
});



app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
