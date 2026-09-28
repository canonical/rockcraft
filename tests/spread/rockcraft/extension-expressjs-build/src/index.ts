import express, { Request, Response, Express } from 'express';
import { writeFileSync } from 'node:fs';

const app: Express = express();

const port: number = 3000;

app.get('/', (req: Request, res: Response) => {
  res.send('Hello World!');
});

app.get('/write-data', (req: Request, res: Response) => {
  writeFileSync('/app-data/expressjs-test.txt', 'written by expressjs\n');
  res.json(true);
});

app.listen(port, () => console.log(`Server listening on :${port}`));
