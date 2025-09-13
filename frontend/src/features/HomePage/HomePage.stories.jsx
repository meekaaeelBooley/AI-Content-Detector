import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import HomePage from './HomePage';

// Storybook configuration for HomePage component
export default {
  title: 'Pages/HomePage',
  component: HomePage,
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: 'The main landing page for the AICD application featuring a hero section with CTA and app preview.',
      },
    },
  },
  tags: ['autodocs'],
  // decorator to wrap stories with Router
  decorators: [
    (Story) => (
      <BrowserRouter>
        <Story />
      </BrowserRouter>
    ),
  ],
};

// Default homepage story
export const Default = {
  parameters: {
    docs: {
      description: {
        story: 'The default homepage layout with purple gradient background, navigation header, and app preview section.',
      },
    },
  },
};