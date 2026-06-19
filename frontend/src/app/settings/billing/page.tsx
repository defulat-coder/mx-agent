import { SettingsPanel } from "@/components/agentos/settings-panel";
import { getSettings } from "@/lib/agentos-api";

export default async function BillingSettingsPage() {
  const settings = await getSettings();
  return <SettingsPanel active="billing" settings={settings} />;
}
