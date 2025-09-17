import Button from './Button';

export default {
  title: 'Components/Button',
  component: Button,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    onClick: { action: 'clicked' },
    children: {
      control: 'text',
      description: 'Button text content',
    },
    disabled: {
      control: 'boolean',
      description: 'Disable the button',
    },
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'success', 'danger'],
      description: 'Button color variant',
    },
    size: {
      control: 'select',
      options: ['small', 'medium', 'large'],
      description: 'Button size',
    },
    borderRadius: {
      control: 'text',
      description: 'Border radius in any CSS unit (px, %, etc)',
    },
    color: {
      control: 'color',
      description: 'Custom text color',
    },
    backgroundColor: {
      control: 'color',
      description: 'Custom background color',
    },
  },
};

// Default button story
export const Primary = {
  args: {
    children: 'Click me',
    disabled: false,
    variant: 'primary',
    size: 'medium',
  },
};

// Secondary variant
export const Secondary = {
  args: {
    children: 'Secondary Button',
    variant: 'secondary',
    size: 'medium',
  },
};

// Success variant
export const Success = {
  args: {
    children: 'Success Button',
    variant: 'success',
    size: 'medium',
  },
};

// Danger variant
export const Danger = {
  args: {
    children: 'Danger Button',
    variant: 'danger',
    size: 'medium',
  },
};

// Disabled state
export const Disabled = {
  args: {
    children: 'Disabled Button',
    disabled: true,
  },
};

// Different sizes
export const Small = {
  args: {
    children: 'Small Button',
    size: 'small',
  },
};

export const Large = {
  args: {
    children: 'Large Button',
    size: 'large',
  },
};

// Custom border radius
export const Rounded = {
  args: {
    children: 'Rounded Button',
    borderRadius: '10px',
  },
};

// Fully customizable
export const Custom = {
  args: {
    children: 'Custom Button',
    borderRadius: '8px',
    color: '#ffffff',
    backgroundColor: '#ff5500',
  },
};