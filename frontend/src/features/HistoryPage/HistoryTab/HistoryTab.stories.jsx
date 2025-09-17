import React from 'react';
import HistoryTab from './HistoryTab';

export default {
  title: 'Components/HistoryTab',
  component: HistoryTab,
  parameters: {
    layout: 'centered',
  },
  argTypes: {
    onClick: { action: 'clicked' },
    isSelected: { control: 'boolean' },
  },
};

const Template = (args) => <HistoryTab {...args} />;

export const TextAnalysis = Template.bind({});
TextAnalysis.args = {
  analysis: {
    id: '1',
    text_preview: 'This is a sample text that was analyzed for AI content. It shows how the detection works with various writing styles and patterns.',
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
  isSelected: false,
};

export const FileAnalysis = Template.bind({});
FileAnalysis.args = {
  analysis: {
    id: '2',
    text_preview: 'Document content analysis showing human writing patterns...',
    timestamp: new Date(Date.now() - 86400000).toISOString(),
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
  },
  isSelected: true,
};

export const HumanWritten = Template.bind({});
HumanWritten.args = {
  analysis: {
    id: '3',
    text_preview: 'This text appears to be written by a human with authentic writing patterns.',
    timestamp: new Date(Date.now() - 172800000).toISOString(),
    text_length: 180,
    source_type: 'text',
    analysis_type: 'single_text',
    result: {
      ai_probability: 0.25,
      human_probability: 0.75,
      confidence: 0.85,
      classification: 'Human-written'
    }
  },
  isSelected: false,
};

export const MixedAnalysis = Template.bind({});
MixedAnalysis.args = {
  analysis: {
    id: '4',
    text_preview: 'This analysis shows mixed results with some AI and some human characteristics.',
    timestamp: new Date(Date.now() - 432000000).toISOString(),
    text_length: 220,
    source_type: 'text',
    analysis_type: 'sentence_level',
    overall_result: {
      overall_ai_probability: 0.55,
      overall_human_probability: 0.45,
      overall_confidence: 0.65,
      overall_classification: 'Mixed'
    }
  },
  isSelected: false,
};