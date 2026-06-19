import { SettingsPanel } from "@/components/agentos/settings-panel";
import { getSettings } from "@/lib/agentos-api";

export default async function RolesSettingsPage() {
  const settings = await getSettings();
  return <SettingsPanel active="roles" settings={settings} />;
}
