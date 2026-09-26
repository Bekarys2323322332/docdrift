# Data sources

DocDrift's "data" is source code and documentation. The hackathon rules ask for data that
is permitted, contains no personal information, no client or confidential data, and nothing
from social media. Every repository used is listed here with its licence.

| Repository | Owner | Licence | Used for |
|---|---|---|---|
| time_forecasting | Me (Beka), my own project | Own work | First audits, real bugs found and fixed, planted-errors benchmark |
| [flask-realworld-example-app](https://github.com/gothinkster/flask-realworld-example-app) | gothinkster / Mohamed Aziz Knani | MIT | Audit of an unfamiliar open-source project |
| [microblog-api](https://github.com/miguelgrinberg/microblog-api) | Miguel Grinberg | MIT | Full pipeline run and re-audit (fix kept local, never pushed) |
| [fastapi-crud-async](https://github.com/testdrivenio/fastapi-crud-async) | testdriven.io / Michael Herman | MIT | One-click audit from the dashboard |
| [node-express-realworld-example-app](https://github.com/gothinkster/node-express-realworld-example-app) | gothinkster | MIT | One-click audit from the dashboard (TypeScript project) |

Notes:
- Only documentation and code were read. No `.env` files or secrets were read (they are
  blocked by `.bobignore`, and cloning a local project copies only committed files).
- Cloned repositories are not redistributed in this repository (see `.gitignore`); only the
  generated reports are kept.
- No personal information, client data, confidential data or social-media data was used.
