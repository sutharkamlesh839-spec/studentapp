import FeaturePage from "@/app/feature-page";

export default async function DynamicWorkspacePage({ params }: { params: Promise<{ segments: string[] }> }) {
  const { segments } = await params;
  return <FeaturePage segments={segments} />;
}
