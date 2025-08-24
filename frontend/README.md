# AICD - AI Content Detector
CSC3003S 2025 Capstone Project
Team: JackBoys

## Members:
Meekaaeel Booley
Zubair Elliot
Mubashir Dawood

## Tech Stack

Frontend Framework: React with JSX
Build Tool: Vite
Styling: CSS3 with custom properties
Icons: React Icons (Material Design)
Routing: React Router DOM
Component Development: Storybook
UI Components: Custom built with accessibility in mind

## Project Architecture

src/
    components/         # Reusable UI components
        Button/             # Interactive button component
        Header/             # Application header with logo
        Icon/               # Custom icon wrapper component
        Metric/             # Circular progress indicator
        Panel/              # Navigation sidebar
        TextInput/          # Input area with file attachment
    features/
        AITextDetectorPage/ # Main application page
    App.jsx             # Root application component
    main.jsx           # Application entry point
    index.css          # Global styles

## Getting started with React+Vite:

npm create vite@latest
    Hint: choose React and then Javascript
cd frontend
npm install

## To start development server:

npm run dev

## Getting started with Storybook:

npm create storybook@latest

## To run Storybook:

npm run storybook

## Additional Dependancies Installed in frontend

npm install react-router-dom  
npm install --save-dev @storybook/react @storybook/react-vite @storybook/addon-essentials @storybook/addon-interactions

npm install react-icons --save

# Component Documentation:

Button: Interactive button with hover, active, and disabled states
Header: Application header with clickable logo
Icon: Custom icon container with size and color props
Metric: Circular progress indicator for score visualization
Panel: Navigation sidebar with selection states
TextInput: Input area with character counting and file attachment

# Build for Production

npm run build

Locate the dist folder and zip contents. Upload zipped contents to AWS Amplify and deploy the website.


# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

