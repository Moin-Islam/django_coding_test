const http = require('http');
const sockjs = require('sockjs');
const cors = require('cors');

const server = http.createServer();

const sockServer = sockjs.createServer({
  prefix: '/sockjs',
  log: (severity, message) => {
    console.log(`[${severity}] ${message}`);
  }
});

// Add CORS headers to SockJS server
const corsOptions = {
  origin: 'http://127.0.0.1:8000',
  methods: ['GET', 'POST'],
  allowedHeaders: ['Content-Type'],
  credentials: true,
  optionsSuccessStatus: 200
};
sockServer.installHandlers(server, { prefix: '/sockjs' });
sockServer.installHandlers(server, { prefix: '/sockjs' }, cors(corsOptions));

sockServer.on('connection', (conn) => {
  console.log('New connection:', conn.id);

  conn.on('data', (message) => {
    console.log('Received message:', message);
  });

  conn.on('close', () => {
    console.log('Connection closed:', conn.id);
  });
});

const port = 8080;
server.listen(port, () => {
  console.log(`SockJS server started on port ${port}`);
});
