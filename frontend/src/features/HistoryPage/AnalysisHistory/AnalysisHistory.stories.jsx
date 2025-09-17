import React from 'react';
import AnalysisHistory from './AnalysisHistory';

export default {
  title: 'Components/AnalysisHistory',
  component: AnalysisHistory,
};

const mockAnalysis = {
  id: 'test-123',
  text_preview: 'This is a sample text preview...',
  timestamp: '2025-09-17T15:34:50.000Z',
  filename: 'sample.docx',
  analysis_type: 'sentence_level',
  source_type: 'file',
  text_length: 542,
  overall_result: {
    overall_ai_probability: 0.85,
    overall_classification: 'AI-generated',
    ai_percentage: 85,
    analyzed_sentences: 3,
    ai_sentence_count: 2,
    human_sentence_count: 1
  },
  sentence_analysis: [
    {
      index: 0,
      sentence: 'This is the first sentence of the analysis.',
      sentence_length: 42,
      result: {
        ai_probability: 0.92,
        human_probability: 0.08,
        confidence: 0.92,
        classification: 'AI-generated'
      }
    },
    {
      index: 1,
      sentence: 'This sentence appears to be written by a human.',
      sentence_length: 48,
      result: {
        ai_probability: 0.15,
        human_probability: 0.85,
        confidence: 0.85,
        classification: 'Human-written'
      }
    },
    {
      index: 2,
      sentence: 'Another AI generated sentence with high probability.',
      sentence_length: 52,
      result: {
        ai_probability: 0.98,
        human_probability: 0.02,
        confidence: 0.98,
        classification: 'AI-generated'
      }
    }
  ]
};

const Template = (args) => <AnalysisHistory {...args} />;

export const Default = Template.bind({});
Default.args = {
  analysis: mockAnalysis,
  onBack: () => console.log('Back clicked')
};

export const NoAnalysisSelected = Template.bind({});
NoAnalysisSelected.args = {
  analysis: null,
  onBack: () => console.log('Back clicked')
};

export const SingleTextAnalysis = Template.bind({});
SingleTextAnalysis.args = {
  analysis: {
    ...mockAnalysis,
    analysis_type: 'single_text',
    result: {
      ai_probability: 0.75,
      human_probability: 0.25,
      confidence: 0.75,
      classification: 'AI-generated'
    },
    sentence_analysis: null
  },
  onBack: () => console.log('Back clicked')
};