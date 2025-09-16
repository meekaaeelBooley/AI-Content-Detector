import React from 'react';
import HistoryPage from './HistoryPage';
import { BrowserRouter } from 'react-router-dom';

export default {
  title: 'Pages/HistoryPage',
  component: HistoryPage,
  parameters: {
    layout: 'fullscreen',
  },
  decorators: [
    (Story) => (
      <BrowserRouter>
        <Story />
      </BrowserRouter>
    ),
  ],
};

const Template = (args) => <HistoryPage {...args} />;

export const Default = Template.bind({});
Default.args = {};

export const WithAnalyses = Template.bind({});
WithAnalyses.parameters = {
  mockData: [
    {
      url: '/api/history',
      method: 'GET',
      status: 200,
      response: {
        success: true,
        analyses: [
          {
            id: '1',
            text_preview: 'This is a sample text that was analyzed for AI content...',
            timestamp: new Date().toISOString(),
            text_length: 150,
            source_type: 'text',
            analysis_type: 'single_text',
            result: {
              ai_probability: 0.85,
              human_probability: 0.15,
              confidence: 0.92,
              classification: 'AI-generated'
            }
          },
          {
            id: '2',
            text_preview: 'Another analysis example with different content...',
            timestamp: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
            text_length: 200,
            source_type: 'file',
            filename: 'document.pdf',
            analysis_type: 'sentence_level',
            overall_result: {
              overall_ai_probability: 0.35,
              overall_human_probability: 0.65,
              overall_confidence: 0.78,
              overall_classification: 'Human-written'
            }
          }
        ],
        total_analyses: 2
      }
    }
  ]
};

export const Empty = Template.bind({});
Empty.parameters = {
  mockData: [
    {
      url: '/api/history',
      method: 'GET',
      status: 200,
      response: {
        success: true,
        analyses: [],
        total_analyses: 0
      }
    }
  ]
};

export const ErrorState = Template.bind({});
ErrorState.parameters = {
  mockData: [
    {
      url: '/api/history',
      method: 'GET',
      status: 500,
      response: {
        error: 'Server error loading history'
      }
    }
  ]
};