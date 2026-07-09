import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { Alert } from "@/components/auth/Alert";
import { EmailRegisterForm } from "@/components/auth/EmailRegisterForm";

describe("Alert", () => {
  it("renders success message with status role", () => {
    render(<Alert variant="success">Account created</Alert>);
    expect(screen.getByRole("status")).toHaveTextContent("Account created");
  });

  it("renders error message with alert role", () => {
    render(<Alert variant="error">Invalid credentials</Alert>);
    expect(screen.getByRole("alert")).toHaveTextContent("Invalid credentials");
  });
});

describe("EmailRegisterForm", () => {
  it("validates required fields", async () => {
    const user = userEvent.setup();
    render(<EmailRegisterForm onSubmit={jest.fn()} />);

    await user.click(screen.getByRole("button", { name: "Create account" }));

    expect(await screen.findByText("Email is required")).toBeInTheDocument();
    expect(screen.getByText("Consent is required")).toBeInTheDocument();
  });

  it("submits valid registration", async () => {
    const user = userEvent.setup();
    const onSubmit = jest.fn().mockResolvedValue({
      message: "Registration successful",
      verification_token: "debug-token",
    });

    render(<EmailRegisterForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText("Email"), "user@chicmatrix.app");
    await user.type(screen.getByLabelText("Password"), "SecurePass123");
    await user.click(screen.getByRole("checkbox"));
    await user.click(screen.getByRole("button", { name: "Create account" }));

    expect(onSubmit).toHaveBeenCalledWith({
      email: "user@chicmatrix.app",
      password: "SecurePass123",
      name: undefined,
      consent_accepted: true,
    });
    expect(await screen.findByText("Registration successful")).toBeInTheDocument();
    expect(screen.getByText("debug-token")).toBeInTheDocument();
  });
});
