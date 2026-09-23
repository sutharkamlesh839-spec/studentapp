import { AppShell } from "@/components/app-shell";
import { FeatureWorkspace } from "@/components/feature-workspace";

export default function FeaturePage({ segments }: { segments: string[] }) {
  return <AppShell><FeatureWorkspace segments={segments} /></AppShell>;
}
