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

// Story showing a sample score result
export const WithScore = Template.bind({});
WithScore.parameters = {
  docs: {
    description: {
      story: 'Page showing a sample AI probability score of 75%.',
    },
  },
};

// Story showing processing/loading state
export const Processing = Template.bind({});
Processing.parameters = {
  docs: {
    description: {
      story: 'Page showing the processing state when content is being analyzed.',
    },
  },
};
