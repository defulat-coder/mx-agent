import { SettingsPanel } from "@/components/agentos/settings-panel";
import { getSettings } from "@/lib/agentos-api";

export default async function OrganizationSettingsPage() {
  const settings = await getSettings();
  return <SettingsPanel active="organization" settings={settings} />;
}
