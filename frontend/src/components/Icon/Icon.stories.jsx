import React from 'react';
import Icon from './Icon';

// Import react-icons directly in the stories file
import { MdAttachFile, MdArrowUpward, MdFavorite } from 'react-icons/md';

// Storybook configuration for Icon component
export default {
  title: 'Components/Icon',
  component: Icon,
  argTypes: {
    // Define controls for Storybook knobs
    size: {
      control: { type: 'number', min: 16, max: 100 }, // Range control for icon size
    },
    color: {
      control: 'color', // Color picker for icon color
    },
    backgroundColor: {
      control: 'color', // Color picker for background
    },
    isClickable: {
      control: 'boolean', // Toggle for clickable state
    },
    isDisabled: {
      control: 'boolean', // Toggle for disabled state
    },
  },
  parameters: {
    // Optional.... Add docs page
    docs: {
      description: {
        component: 'A customizable icon component with multiple states and styles.',
      },
    },
  },
};

// Reusable template for all icon stories
const Template = (args) => <Icon {...args} />;

// Set default args for all stories
Template.args = {
  size: 40,
  color: '#8E12D5', // Default purple color
  backgroundColor: 'white',
  isClickable: true,
  isDisabled: false,
};

// Individual story variations demonstrating different props
export const Paperclip = Template.bind({});
Paperclip.args = {
  ...Template.args,
  icon: MdAttachFile, // Attachment icon example
};

export const ArrowUp = Template.bind({});
ArrowUp.args = {
  ...Template.args,
  icon: MdArrowUpward,
  color: 'white', // White icon on colored background
  backgroundColor: '#8E12D5',
};

export const Heart = Template.bind({});
Heart.args = {
  ...Template.args,
  icon: MdFavorite,
  color: '#FF3366', // Custom pink color for heart
};

export const Disabled = Template.bind({});
Disabled.args = {
  ...Template.args,
  icon: MdArrowUpward,
  isDisabled: true, // Disabled state example
  backgroundColor: '#f0f0f0', // Light gray background for disabled state
};

export const NonClickable = Template.bind({});
NonClickable.args = {
  ...Template.args,
  icon: MdAttachFile,
  isClickable: false, // Non-interactive icon example
};

export const CustomSize = Template.bind({});
CustomSize.args = {
  ...Template.args,
  icon: MdFavorite,
  size: 60, // Larger icon size example
  color: 'white',
  backgroundColor: '#8E12D5',
};