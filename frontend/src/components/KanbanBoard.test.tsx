import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi, beforeEach, afterEach } from "vitest";
import { KanbanBoard } from "@/components/KanbanBoard";
import { initialData } from "@/lib/kanban";

const mockFetch = (board = initialData) => {
  vi.stubGlobal(
    "fetch",
    vi.fn((url: string, opts?: RequestInit) => {
      if (url === "/api/board" && !opts?.method) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(board),
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    })
  );
};

beforeEach(() => mockFetch());
afterEach(() => vi.unstubAllGlobals());

const onLogout = vi.fn();

const getFirstColumn = () => screen.getAllByTestId(/column-/i)[0];

describe("KanbanBoard", () => {
  it("renders five columns after load", async () => {
    render(<KanbanBoard onLogout={onLogout} />);
    expect(await screen.findAllByTestId(/column-/i)).toHaveLength(5);
  });

  it("renames a column", async () => {
    render(<KanbanBoard onLogout={onLogout} />);
    await screen.findAllByTestId(/column-/i);
    const column = getFirstColumn();
    const input = within(column).getByLabelText("Column title");
    await userEvent.clear(input);
    await userEvent.type(input, "New Name");
    expect(input).toHaveValue("New Name");
  });

  it("adds and removes a card", async () => {
    render(<KanbanBoard onLogout={onLogout} />);
    await screen.findAllByTestId(/column-/i);
    const column = getFirstColumn();
    await userEvent.click(
      within(column).getByRole("button", { name: /add a card/i })
    );
    await userEvent.type(
      within(column).getByPlaceholderText(/card title/i),
      "New card"
    );
    await userEvent.type(
      within(column).getByPlaceholderText(/details/i),
      "Notes"
    );
    await userEvent.click(
      within(column).getByRole("button", { name: /add card/i })
    );
    expect(within(column).getByText("New card")).toBeInTheDocument();

    await userEvent.click(
      within(column).getByRole("button", { name: /delete new card/i })
    );
    expect(within(column).queryByText("New card")).not.toBeInTheDocument();
  });
});
