import TextInput from "./TextInput";

// Storybook configuration for TextInput component
export default {
  title: "Components/TextInput",
  component: TextInput,
};

// Default story with demo handlers
export const Default = {
  args: {
    onSubmit: (text) => alert(`Submitted: ${text}`), // Demo submission handler
    onFileAttach: (file) => alert(`File attached: ${file.name}`), // Demo file attachment handler
  },
};