import Button from './Button';

// Storybook configuration for Button component
export default {
  title: 'Components/Button', // Storybook navigation path
  component: Button,
  parameters: {
    layout: 'centered', // Center the component in the canvas
  },
  tags: ['autodocs'], // Enable automatic documentation generation
  argTypes: {
    // Define control types and descriptions for Storybook controls
    onClick: { action: 'clicked' }, // Action logger for click events
    children: {
      control: 'text', // Text input control for button content
      description: 'Button text content',
    },
    disabled: {
      control: 'boolean', // Toggle control for disabled state
      description: 'Disable the button',
    },
  },
};

// Default button story with basic configuration
export const Primary = {
  args: {
    children: 'Click me',
    disabled: false,
  },
};

// Secondary variant story
export const Secondary = {
  args: {
    children: 'Secondary Button',
    disabled: false,
  },
};

// Disabled state demonstration
export const Disabled = {
  args: {
    children: 'Disabled Button',
    disabled: true,
  },
};

// Story showing custom text content
export const WithCustomText = {
  args: {
    children: 'Custom Button Text',
    disabled: false,
  },
};