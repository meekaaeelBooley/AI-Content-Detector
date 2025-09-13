import React from 'react';
import AITextDetectorPage from './AITextDetectorPage';

// Storybook configuration for the main page component
export default {
  title: 'Pages/AITextDetectorPage',
  component: AITextDetectorPage,
  parameters: {
    layout: 'fullscreen', // Use full browser width
    docs: {
      description: {
        component: 'Main page for AI text detection featuring a header, navigation panel, text input area, and metrics display.',
      },
    },
  },
};

// Reusable template for all stories
const Template = (args) => <AITextDetectorPage {...args} />;

// Default empty state story
export const Default = Template.bind({});
Default.args = {};


