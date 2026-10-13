# PriceBiz

**Making prices more transparent across Africa.**

PriceBiz is a price intelligence platform designed to help consumers and businesses across Africa make informed pricing decisions through location-based price information for everyday products and services.

Starting in Nigeria, PriceBiz aims to make it easier to discover, compare, and validate prices across different markets and locations. By turning price observations into actionable insights, the platform seeks to help consumers understand prevailing market prices, help businesses assess their pricing decisions, and improve access to reliable local price information.

Our long-term vision is to build a trusted source of price intelligence that makes markets more transparent, empowers better purchasing decisions, and supports data-driven commerce across Africa.

## Live Application

- **Frontend:** https://price-biz.vercel.app/
- **Backend API:** https://pricebiz-backend.onrender.com
- **API Documentation:** https://pricebiz-backend.onrender.com/docs

*The API documentation link is available only if Swagger UI is enabled in the backend configuration.*

## Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Objectives](#objectives)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Overview

PriceBiz focuses on making local price information more accessible and useful. It is designed to support product discovery, location-based price comparisons, and analysis of observed prices.

The platform begins with Nigeria, with a long-term goal of expanding price intelligence coverage across African markets.

## Problem Statement

Prices for everyday products and services can vary significantly across markets, sellers, and geographical locations. However, reliable and accessible information about these differences is often difficult to obtain, particularly in markets where many transactions take place through informal channels and local retailers have limited online visibility.

This lack of accessible price information can make it difficult for consumers to determine whether a quoted price is reasonable and for businesses to evaluate their pricing decisions against prevailing market conditions.

PriceBiz aims to address this challenge by providing a platform for collecting, organizing, analyzing, and presenting location-based price information.

## Objectives

PriceBiz aims to:

- **Improve price transparency:** Make local price information easier to discover and understand.
- **Support informed purchasing:** Help consumers compare observed prices across locations.
- **Enable pricing decisions:** Give businesses insights into observed market prices.
- **Build local price intelligence:** Organize price observations into useful, location-specific information.
- **Support African markets:** Begin with Nigeria and build toward broader coverage across Africa.

## Key Features

PriceBiz is being developed around the following capabilities:

- **Product discovery:** Find products and their associated price information.
- **Location-based price information:** Explore observed prices across supported geographical areas.
- **Price analysis:** Generate insights from available price observations.
- **Community contributions:** Support the collection of price information from different sources.
- **Price discussions and feedback:** Provide mechanisms for users to engage with price-related information.
- **Data validation and moderation:** Help maintain the quality and reliability of submitted information.

Feature availability may vary as development progresses.

## Technology Stack

### Backend

- Python
- FastAPI
- MongoDB
- Pydantic
- `uv` for Python project and dependency management

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- Axios for HTTP requests

### Infrastructure and Deployment

- **Vercel:** Frontend hosting
- **Render:** Backend hosting
- **MongoDB Atlas:** Managed database hosting
- **Git and GitHub:** Version control and source hosting

## Project Structure

The project is organized into separate backend and frontend applications.

```text
PriceBiz/
├── backend/
│   ├── app/
│   │   ├── controllers/
│   │   ├── routes/
│   │   ├── services/
│   │   └── ...
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── uv.lock
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── ...
├── .gitignore
└── README.md
```

This structure is representative; individual files and directories may differ as the project evolves.

## Getting Started

### Prerequisites

Install the following tools before setting up PriceBiz:

- Python version supported by the backend configuration
- Node.js and npm
- MongoDB, locally or through a managed service
- `uv` for Python dependency management
- Git

### Clone the Repository

```bash
git clone https://github.com/codira300/PriceBiz.git
cd PriceBiz
```

### Backend Setup

```bash
cd backend
uv sync
```

Configure the required backend environment variables before starting the application.

### Frontend Setup

Open a separate terminal from the project root:

```bash
cd frontend
npm install
```

## Configuration

PriceBiz uses environment variables to configure application behavior and protect sensitive settings.

### Frontend Environment Variables

Create a `.env.local` file inside the `frontend` directory for local development:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

For production, configure the following environment variable in Vercel:

```env
VITE_API_BASE_URL=https://pricebiz-backend.onrender.com
```

Vite exposes variables prefixed with `VITE_` to frontend code. **Never store database credentials, JWT signing secrets, or other private backend credentials in frontend environment variables.**

After changing environment variables, restart the local development server or redeploy the frontend as appropriate.

### Backend Environment Variables

Configure the backend's required environment variables in your local environment or Render dashboard. These include the MongoDB connection string, database name, JWT settings, and any other variables required by the backend configuration.

Keep all secrets out of version control. Use `.env` files locally and Render environment settings in production.

## Running the Application

### Start the Backend

From the `backend` directory:

```bash
uv run uvicorn app.main:app --reload
```

The local API will typically be available at:

```text
http://127.0.0.1:8000
```

### Start the Frontend

From the `frontend` directory:

```bash
npm run dev
```

Open the local URL printed by Vite in your terminal.

## Deployment

PriceBiz currently uses separate services for its frontend, backend, and database.

| Component | Platform |
|---|---|
| Frontend | Vercel |
| Backend API | Render |
| Database | MongoDB Atlas |

### Frontend Deployment

The frontend is deployed to Vercel at:

https://price-biz.vercel.app/

Configure the `VITE_API_BASE_URL` environment variable in the Vercel project settings to point to the deployed backend API.

### Backend Deployment

The backend is deployed to Render at:

https://pricebiz-backend.onrender.com

Ensure the service has the required environment variables and can connect to MongoDB Atlas.

### Cross-Origin Resource Sharing (CORS)

The backend must allow requests from the deployed frontend origin:

```text
https://price-biz.vercel.app
```

Configure FastAPI CORS middleware to allow the production frontend origin and any required local development origins. Avoid using unrestricted origins in production when credentials are involved.

## API Documentation

PriceBiz uses FastAPI for its backend API. When the application is running and documentation is enabled, interactive documentation is available at:

- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`

For the deployed backend, visit:

https://pricebiz-backend.onrender.com/docs

## Testing

Run the tests configured for each application before submitting changes.

### Backend

From the `backend` directory:

```bash
uv run pytest
```

### Frontend

From the `frontend` directory, inspect the available npm scripts:

```bash
npm run
```

Run the configured lint, test, and build commands as appropriate. A successful build alone does not guarantee that all features, API integrations, or authentication flows work correctly.

## Contributing

Contributions that improve price-data quality, application reliability, security, accessibility, and user experience are welcome.

1. Fork the repository or create a feature branch.
2. Make a focused change.
3. Add or update tests where appropriate.
4. Run the relevant checks.
5. Submit a pull request describing the change and its purpose.

Please do not include credentials, private user data, or other sensitive information in commits or issue reports.

## License

The project's license has not yet been specified. Until a license is added to the repository, do not assume that the source code is available for unrestricted reuse or redistribution.
