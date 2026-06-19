import { SettingsPanel } from "@/components/agentos/settings-panel";
import { getSettings } from "@/lib/agentos-api";

export default async function ProfileSettingsPage() {
  const settings = await getSettings();
  return <SettingsPanel active="profile" settings={settings} />;
}
