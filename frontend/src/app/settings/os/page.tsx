import { SettingsPanel } from "@/components/agentos/settings-panel";
import { getSettings } from "@/lib/agentos-api";

export default async function OSSettingsPage() {
  const settings = await getSettings();
  return <SettingsPanel active="os" settings={settings} />;
}
