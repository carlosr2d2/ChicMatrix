import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { EmailLoginForm } from "@/components/auth/EmailLoginForm";
import { MethodTabs } from "@/components/auth/MethodTabs";
import { SocialLoginButtons } from "@/components/auth/SocialLoginButtons";

describe("MethodTabs", () => {
  it("renders tab panels", async () => {
    const user = userEvent.setup();
    render(
      <MethodTabs tabs={[{ id: "a", label: "Email" }, { id: "b", label: "Phone" }]}>
        <div>Email panel</div>
        <div>Phone panel</div>
      </MethodTabs>,
    );

    expect(screen.getByText("Email panel")).toBeInTheDocument();
    await user.click(screen.getByRole("tab", { name: "Phone" }));
    expect(screen.getByText("Phone panel")).toBeInTheDocument();
  });
});

describe("EmailLoginForm", () => {
  it("submits credentials", async () => {
    const user = userEvent.setup();
    const onSubmit = jest.fn().mockResolvedValue(undefined);

    render(<EmailLoginForm onSubmit={onSubmit} />);
    await user.type(screen.getByLabelText("Email"), "user@chicmatrix.app");
    await user.type(screen.getByLabelText("Password"), "SecurePass123");
    await user.click(screen.getByRole("button", { name: "Sign in" }));

    expect(onSubmit).toHaveBeenCalledWith({
      email: "user@chicmatrix.app",
      password: "SecurePass123",
    });
  });
});

describe("SocialLoginButtons", () => {
  it("uses debug token in development mode", async () => {
    const user = userEvent.setup();
    const onSuccess = jest.fn();
    const original = process.env.NEXT_PUBLIC_SOCIAL_AUTH_DEBUG;
    process.env.NEXT_PUBLIC_SOCIAL_AUTH_DEBUG = "true";

    render(
      <SocialLoginButtons mode="login" consentAccepted onSuccess={onSuccess} />,
    );

    await user.click(screen.getByRole("button", { name: "Continue with Google" }));
    expect(onSuccess).toHaveBeenCalledWith(
      "google",
      expect.stringContaining("debug-google:"),
    );

    process.env.NEXT_PUBLIC_SOCIAL_AUTH_DEBUG = original;
  });
});
