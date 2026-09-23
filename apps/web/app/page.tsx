import { AppShell } from "@/components/app-shell";
import { DashboardView } from "@/components/dashboard-view";
import { demoDashboard } from "@/lib/dashboard-data";

export default function HomePage() {
  return (
    <AppShell>
      <DashboardView snapshot={demoDashboard} />
    </AppShell>
  );
}
