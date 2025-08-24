import React, { useState } from "react";
import Icon from "../Icon/Icon"; // adjust path if needed
import { MdAttachFile, MdArrowUpward } from "react-icons/md";

// Text input component with character counter, file attachment, and submit functionality
const TextInput = ({ onSubmit, onFileAttach }) => {
  const [text, setText] = useState("");
  const maxChars = 1000; // Maximum allowed characters

  const handleChange = (e) => setText(e.target.value);

  const handleSubmit = () => {
    if (text.trim() && text.length <= maxChars) {
      onSubmit?.(text); // Call onSubmit callback if provided
      setText(""); // Clear input after submission
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && onFileAttach) {
      const validTypes = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document", // .docx
        "text/plain", // .txt
      ];
      if (validTypes.includes(file.type)) {
        onFileAttach(file); // Pass valid file to parent
      } else {
        alert("Invalid file type. Please attach a .docx, .pdf, or .txt file.");
      }
    }
  };

  const isDisabled = !text.trim() || text.length > maxChars; // Disable submit if empty or over limit

  return (
    <div
      style={{
        border: "1px solid black",
        borderRadius: "10px",
        backgroundColor: "white",
        display: "flex",
        flexDirection: "column",
        position: "relative",
        width: "100%",
        height: "100%", // Fill available container space
        padding: "0.5rem",
        boxSizing: "border-box", // Include padding in width/height
      }}
    >
      {/* Main text input area */}
      <textarea
        value={text}
        onChange={handleChange}
        placeholder="Type here..."
        style={{
          flex: 1, // Take up remaining vertical space
          border: "none",
          outline: "none",
          resize: "none", // Disable manual resizing
          fontSize: "1rem",
          color: "black",
          backgroundColor: "transparent",
        }}
      />

      {/* Footer with counter and action buttons */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginTop: "0.25rem",
        }}
      >
        {/* Character counter with error state */}
        <span
          style={{
            fontSize: "0.85rem",
            color: text.length > maxChars ? "red" : "black", // Red when over limit
          }}
        >
          {text.length}/{maxChars} characters
        </span>

        {/* Action buttons container */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          {/* Hidden file input with icon trigger */}
          <label>
            <input
              type="file"
              accept=".docx,.pdf,.txt" // Restrict file types
              style={{ display: "none" }}
              onChange={handleFileChange}
            />
            <Icon
              icon={MdAttachFile}
              size={36}
              color="black"
              backgroundColor="white"
              isClickable={true}
              isDisabled={false}
            />
          </label>

          {/* Submit button with disabled state */}
          <Icon
            icon={MdArrowUpward}
            size={36}
            color="white"
            backgroundColor="#8E12D5" // Purple background
            isClickable={!isDisabled}
            isDisabled={isDisabled}
            onClick={handleSubmit}
          />
        </div>
      </div>
    </div>
  );
};

export default TextInput;