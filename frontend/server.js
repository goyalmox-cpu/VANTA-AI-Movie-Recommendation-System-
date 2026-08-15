const http = require('http');
const fs = require('fs');
const path = require('path');

const root = __dirname;
const types = {
  '.css': 'text/css; charset=utf-8',
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.png': 'image/png',
};

http.createServer((request, response) => {
  let file = decodeURIComponent(request.url.split('?')[0]);
  if (file === '/' || file === '') file = '/index.html';

  const target = path.resolve(root, `.${file}`);
  if (!target.startsWith(root)) {
    response.writeHead(403);
    return response.end('Forbidden');
  }

  fs.readFile(target, (error, content) => {
    if (error) {
      response.writeHead(404);
      return response.end('Not found');
    }
    response.writeHead(200, { 'Content-Type': types[path.extname(target)] || 'application/octet-stream' });
    response.end(content);
  });
}).listen(5173, '127.0.0.1', () => console.log('VANTA frontend: http://127.0.0.1:5173'));
