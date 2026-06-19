"use client";

import { Check, Copy, ExternalLink, KeyRound, Plus, ShieldCheck, Trash2 } from "lucide-react";
import { type ReactNode, useMemo, useState } from "react";

import type { SettingsResponse } from "@/lib/agentos-types";
import { cn } from "@/lib/utils";

type SettingsPage = keyof SettingsResponse | "roles";
type SaveState = "idle" | "dirty" | "saved";

const inputClass =
  "h-9 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm text-neutral-950 outline-none transition-colors placeholder:text-neutral-400 focus:border-neutral-400 disabled:bg-neutral-50 disabled:text-neutral-400";
const labelClass = "font-mono text-[11px] uppercase tracking-normal text-neutral-500";
const buttonClass =
  "inline-flex h-9 items-center justify-center gap-2 rounded-md border border-neutral-200 px-4 font-mono text-[11px] uppercase text-neutral-800 transition-colors hover:bg-neutral-100 disabled:cursor-not-allowed disabled:bg-neutral-50 disabled:text-neutral-400";

const roleRows = [
  "Admin",
  "Member",
  "Viewer",
  "Billing Manager",
  "Custom Role",
  "Support Lead",
  "Auditor",
  "Developer",
  "Custom Role",
];

const billingColumns = [
  {
    action: "Current tier",
    disabled: true,
    kicker: "Free",
    price: "Current tier",
    sections: [
      ["Open source", "Build multi-agent systems", "Run agent systems using Agent OS"],
      ["Control plane for your local AgentOS", "Chat with agents, teams and workflows", "Session monitoring & metrics", "Knowledge & memory management", "System evaluations"],
      ["Jumpstart & community", "Pre-built production-ready codebases", "Community support & forums"],
    ],
  },
  {
    action: "Upgrade to Pro",
    kicker: "Pro",
    price: "$150 per month",
    sections: [
      ["Everything in Free"],
      ["Control plane for live AgentOS", "1 live AgentOS connection", "4 free member invites", "Shared AgentOS access", "Role & permission control"],
      ["Unlimited usage", "Monitoring, retention, knowledge and more"],
      ["Add-ons", "$30/mo per seat", "$95/mo per live connection"],
    ],
  },
  {
    action: "Book a call",
    kicker: "Enterprise",
    price: "Contact us",
    sections: [
      ["Everything in Pro"],
      ["Support & scale", "Dedicated Slack channel", "Dedicated technical lead", "Support SLA"],
      ["Customization", "Custom SSO and RBAC", "Custom agent solutions", "Self-hosted control plane"],
    ],
  },
];

function asString(value: unknown, fallback: string) {
  return typeof value === "string" && value.length > 0 ? value : fallback;
}

function asNumber(value: unknown, fallback: number) {
  return typeof value === "number" ? value : fallback;
}

function SaveButton({ state, onSave }: { state: SaveState; onSave: () => void }) {
  return (
    <button
      className={cn(buttonClass, "min-w-28", state === "dirty" && "border-neutral-950 bg-neutral-950 text-white hover:bg-neutral-800")}
      disabled={state === "idle"}
      onClick={onSave}
      type="button"
    >
      {state === "saved" ? "Saved" : "Save"}
    </button>
  );
}

function Field({
  children,
  label,
  wide = false,
}: {
  children: ReactNode;
  label: string;
  wide?: boolean;
}) {
  return (
    <label className={cn("block space-y-2", wide ? "max-w-4xl" : "max-w-xl")}>
      <span className={labelClass}>{label}</span>
      {children}
    </label>
  );
}

function Toggle({ checked, onToggle }: { checked: boolean; onToggle: () => void }) {
  return (
    <button
      aria-pressed={checked}
      className={cn(
        "relative h-5 w-9 rounded-full border border-neutral-200 bg-neutral-200 transition-colors",
        checked && "border-neutral-900 bg-neutral-900",
      )}
      onClick={onToggle}
      type="button"
    >
      <span
        className={cn(
          "absolute left-0.5 top-0.5 size-4 rounded-full bg-white shadow-sm transition-transform",
          checked && "translate-x-4",
        )}
      />
    </button>
  );
}

export function SettingsPanel({
  active,
  settings,
}: {
  active: SettingsPage;
  settings: SettingsResponse;
}) {
  const title = active === "os" ? "OS & Security" : active === "roles" ? "Roles" : active[0].toUpperCase() + active.slice(1);

  return (
    <div className="min-h-0 flex-1 overflow-auto bg-white px-5 py-5">
      <div className="mb-5">
        <h1 className="text-xl font-semibold">{title}</h1>
      </div>

      {active === "profile" ? <ProfileSettings settings={settings} /> : null}
      {active === "organization" ? <OrganizationSettings settings={settings} /> : null}
      {active === "os" ? <OSSecuritySettings settings={settings} /> : null}
      {active === "roles" ? <RolesSettings /> : null}
      {active === "billing" ? <BillingSettings /> : null}
    </div>
  );
}

function ProfileSettings({ settings }: { settings: SettingsResponse }) {
  const [saveState, setSaveState] = useState<SaveState>("idle");
  const profile = settings.profile;
  const [name, setName] = useState(asString(profile.name, "MX Operator"));
  const [username, setUsername] = useState(asString(profile.username, "mx-operator"));
  const email = asString(profile.email, "operator@mx.local");
  const markDirty = () => setSaveState("dirty");

  return (
    <div className="space-y-5">
      <Field label="Name">
        <input className={inputClass} onChange={(event) => { setName(event.target.value); markDirty(); }} placeholder="John Doe" value={name} />
      </Field>
      <Field label="User name">
        <input className={inputClass} onChange={(event) => { setUsername(event.target.value); markDirty(); }} placeholder="johndoe123" value={username} />
      </Field>
      <Field label="Email">
        <input className={inputClass} disabled placeholder="name@company.com" type="email" value={email} />
      </Field>
      <SaveButton onSave={() => setSaveState("saved")} state={saveState} />
    </div>
  );
}

function OrganizationSettings({ settings }: { settings: SettingsResponse }) {
  const organization = settings.organization;
  const [name, setName] = useState(asString(organization.name, "MX Agent"));
  const [saveState, setSaveState] = useState<SaveState>("idle");
  const [tab, setTab] = useState<"members" | "pending">("members");
  const members = asNumber(organization.members, 1);
  const pendingInvites = asNumber(organization.pending_invites, 0);

  return (
    <div className="max-w-5xl space-y-5">
      <Field label="Name">
        <input
          className={inputClass}
          onChange={(event) => {
            setName(event.target.value);
            setSaveState("dirty");
          }}
          placeholder="Your organization name"
          value={name}
        />
      </Field>
      <SaveButton onSave={() => setSaveState("saved")} state={saveState} />

      <section className="rounded-lg border border-neutral-200 bg-white p-6 shadow-[0_8px_24px_rgba(0,0,0,0.06)]">
        <div className="mb-4 flex items-center gap-2">
          <h2 className="text-lg font-semibold">Invite new organization members</h2>
          <span className="rounded-md bg-red-50 px-2 py-1 font-mono text-[10px] uppercase text-[#ff3b25]">Pro</span>
        </div>
        <p className="mb-5 text-sm text-neutral-600">
          Upgrade to unlock multi-user access, role management, and a shared live AgentOS.
        </p>
        <p className="mb-3 text-sm font-medium">Benefits</p>
        <div className="grid max-w-2xl gap-3 text-sm text-neutral-700 sm:grid-cols-2">
          {["1 live AgentOS connection", "Role & permission control", "3 free member invites", "Shared AgentOS access"].map((item) => (
            <span className="flex items-center gap-2" key={item}>
              <Check className="size-3.5 text-[#ff3b25]" />
              {item}
            </span>
          ))}
        </div>
        <button className={cn(buttonClass, "mt-5 border-neutral-950 bg-neutral-950 text-white hover:bg-neutral-800")} type="button">
          Upgrade to Pro
        </button>
      </section>

      <section className="border-t border-neutral-100 pt-5">
        <div className="mb-4 flex items-center gap-2 text-sm">
          <button className={cn("rounded-md px-2 py-1", tab === "members" && "bg-neutral-100 font-medium")} onClick={() => setTab("members")} type="button">
            Members <span className="ml-1 rounded-full bg-neutral-100 px-2">{members}</span>
          </button>
          <button className={cn("rounded-md px-2 py-1", tab === "pending" && "bg-neutral-100 font-medium")} onClick={() => setTab("pending")} type="button">
            Pending invites <span className="ml-1 rounded-full bg-neutral-100 px-2">{pendingInvites}</span>
          </button>
        </div>
        <div className="max-w-4xl rounded-lg border border-neutral-100">
          {tab === "members" ? (
            <div className="grid grid-cols-[1fr_140px_120px] items-center gap-4 px-4 py-4 text-sm">
              <span className="font-medium">MX Operator</span>
              <span className="font-mono text-[11px] uppercase text-neutral-500">Owner</span>
              <span className="text-right text-neutral-500">Active</span>
            </div>
          ) : (
            <div className="px-4 py-8 text-sm text-neutral-500">No pending invitations.</div>
          )}
        </div>
        <button className={cn(buttonClass, "mt-5 border-red-200 text-red-600 hover:bg-red-50")} type="button">
          <Trash2 className="size-3.5" />
          Delete organization
        </button>
      </section>
    </div>
  );
}

function OSSecuritySettings({ settings }: { settings: SettingsResponse }) {
  const os = settings.os;
  const initialTags = useMemo(() => (Array.isArray(os.tags) ? os.tags.map(String) : ["LOCAL", "PRODUCTION"]), [os.tags]);
  const [saveState, setSaveState] = useState<SaveState>("idle");
  const [name, setName] = useState(asString(os.name, "MX AgentOS"));
  const [protocol, setProtocol] = useState(asString(os.protocol, "http://"));
  const [endpoint, setEndpoint] = useState(asString(os.endpoint_host, asString(os.endpoint_url, "localhost:8000").replace(/^https?:\/\//, "")));
  const [authorization, setAuthorization] = useState(asString(os.authorization, "jwt") === "jwt");
  const [description, setDescription] = useState(asString(os.description, ""));
  const [tags, setTags] = useState(initialTags);
  const [tagValue, setTagValue] = useState("");
  const [headerName, setHeaderName] = useState("");
  const [headerValue, setHeaderValue] = useState("");
  const osId = asString(os.id, "mx-agent");
  const markDirty = () => setSaveState("dirty");

  return (
    <div className="max-w-5xl space-y-5 pb-12">
      <Field label="AgentOS name" wide>
        <input className={inputClass} onChange={(event) => { setName(event.target.value); markDirty(); }} placeholder="Your AgentOS name" value={name} />
      </Field>
      <Field label="AgentOS ID" wide>
        <div className="flex">
          <input className={cn(inputClass, "rounded-r-none font-mono")} disabled value={osId} />
          <button aria-label="Copy AgentOS ID" className={cn(buttonClass, "rounded-l-none px-3")} type="button">
            <Copy className="size-3.5" />
          </button>
        </div>
      </Field>
      <Field label="Endpoint URL" wide>
        <div className="grid grid-cols-[92px_1fr]">
          <select
            className={cn(inputClass, "rounded-r-none border-r-0 font-mono")}
            onChange={(event) => {
              setProtocol(event.target.value);
              markDirty();
            }}
            value={protocol}
          >
            <option>http://</option>
            <option>https://</option>
          </select>
          <input className={cn(inputClass, "rounded-l-none")} onChange={(event) => { setEndpoint(event.target.value); markDirty(); }} placeholder="localhost:8000" value={endpoint} />
        </div>
      </Field>

      <section className="max-w-4xl border-l border-neutral-200 pl-5">
        <button className="mb-4 flex items-center gap-2 font-mono text-[11px] uppercase text-neutral-600" type="button">
          <ShieldCheck className="size-3.5" />
          Authorization
        </button>
        <div className="mb-3 flex items-center gap-3">
          <span className={labelClass}>Token-based authorization (JWT)</span>
          <Toggle checked={authorization} onToggle={() => { setAuthorization((value) => !value); markDirty(); }} />
        </div>
        <p className="mb-5 max-w-3xl text-sm text-neutral-500">
          Turn on user authorization for your OS using JWT tokens. Set the generated public key as JWT_VERIFICATION_KEY in your environment.
        </p>
        <div className="my-4 flex items-center gap-4 text-xs text-neutral-400">
          <span className="h-px flex-1 bg-neutral-200" />
          OR
          <span className="h-px flex-1 bg-neutral-200" />
        </div>
        <Field label="Security key" wide>
          <div className="grid grid-cols-[1fr_44px] gap-2">
            <input className={inputClass} disabled placeholder="Set or generate a security key" value="" />
            <button aria-label="Generate security key" className={buttonClass} type="button">
              <KeyRound className="size-3.5" />
            </button>
          </div>
        </Field>
        <p className="mt-2 text-sm text-neutral-500">Set the security key as OS_SECURITY_KEY in your .env file or export it in your terminal.</p>
      </section>

      <section className="max-w-4xl border-l border-neutral-200 pl-5">
        <p className={cn(labelClass, "mb-5")}>Additional settings</p>
        <Field label="Description" wide>
          <textarea
            className={cn(inputClass, "min-h-16 resize-none py-3")}
            onChange={(event) => { setDescription(event.target.value); markDirty(); }}
            placeholder="Add a description for your AgentOS"
            value={description}
          />
        </Field>
        <div className="mt-5 space-y-2">
          <span className={labelClass}>Tags</span>
          <div className="flex flex-wrap gap-2">
            {tags.map((tag) => (
              <span className="rounded-md border border-neutral-200 px-2 py-1 font-mono text-[11px] uppercase text-neutral-700" key={tag}>
                {tag}
              </span>
            ))}
          </div>
          <div className="grid max-w-xl grid-cols-[1fr_100px] gap-2">
            <input className={inputClass} onChange={(event) => setTagValue(event.target.value)} placeholder="Add tags to make your AgentOS easier to spot" value={tagValue} />
            <button
              className={buttonClass}
              disabled={!tagValue}
              onClick={() => {
                setTags((current) => [...current, tagValue.toUpperCase()]);
                setTagValue("");
                markDirty();
              }}
              type="button"
            >
              Add tag
            </button>
          </div>
        </div>
        <div className="mt-5 space-y-2">
          <span className={labelClass}>Custom headers</span>
          <div className="grid max-w-4xl gap-2 sm:grid-cols-2">
            <input className={inputClass} onChange={(event) => { setHeaderName(event.target.value); markDirty(); }} placeholder="Header name (e.g., X-Custom-Auth)" value={headerName} />
            <input className={inputClass} onChange={(event) => { setHeaderValue(event.target.value); markDirty(); }} placeholder="Header value" value={headerValue} />
          </div>
        </div>
      </section>

      <div className="flex items-center gap-3">
        <SaveButton onSave={() => setSaveState("saved")} state={saveState} />
        <button className={cn(buttonClass, "border-red-200 text-red-600 hover:bg-red-50")} type="button">
          <Trash2 className="size-3.5" />
          Delete AgentOS
        </button>
      </div>
    </div>
  );
}

function RolesSettings() {
  return (
    <div className="relative min-h-[620px] max-w-6xl overflow-hidden">
      <div className="grid gap-5 blur-[3px] sm:grid-cols-2 xl:grid-cols-3">
        {roleRows.map((role, index) => (
          <div className="flex h-16 items-center gap-3 rounded-lg border border-neutral-200 bg-white px-4" key={`${role}-${index}`}>
            <span className="flex-1 font-mono text-[11px] uppercase text-neutral-700">{role}</span>
            <button className={buttonClass} type="button">Manage</button>
            <button className={cn(buttonClass, "border-red-200 bg-red-50 text-red-600")} type="button">Delete</button>
          </div>
        ))}
        <button className="flex h-16 items-center justify-center gap-2 rounded-lg border border-dashed border-neutral-200 bg-white font-mono text-[11px] uppercase text-neutral-800" type="button">
          <Plus className="size-4" />
          Add new role
        </button>
      </div>
      <div className="absolute inset-0 grid place-items-center bg-white/55">
        <div className="max-w-md text-center">
          <div className="mb-5 inline-flex items-center gap-2">
            <span className="grid size-10 place-items-center rounded-full bg-neutral-950 text-white">
              <ShieldCheck className="size-5" />
            </span>
            <span className="grid size-10 place-items-center rounded-full bg-[#ff3b25] text-white">
              <KeyRound className="size-5" />
            </span>
          </div>
          <h2 className="text-2xl font-semibold">Upgrade to use this feature</h2>
          <p className="mt-2 text-sm text-neutral-600">This feature requires an Enterprise account to be used.</p>
          <div className="mt-6 flex justify-center gap-2">
            <button className={buttonClass} type="button">
              Learn more
              <ExternalLink className="size-3.5" />
            </button>
            <button className={cn(buttonClass, "border-neutral-950 bg-neutral-950 text-white hover:bg-neutral-800")} type="button">
              Contact sales
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function BillingSettings() {
  return (
    <div className="grid max-w-7xl overflow-hidden rounded-lg border border-neutral-200 lg:grid-cols-3">
      {billingColumns.map((column) => (
        <section className="flex min-h-[530px] flex-col border-b border-neutral-200 p-6 last:border-b-0 lg:border-b-0 lg:border-r lg:last:border-r-0" key={column.kicker}>
          <p className={labelClass}>{column.kicker}</p>
          <h2 className="mt-3 text-xl font-medium">{column.price}</h2>
          <div className="mt-7 flex-1 space-y-5">
            {column.sections.map((section) => (
              <div className="space-y-3" key={section.join("-")}>
                {section.map((item, index) => (
                  <p className={cn("flex items-center gap-2 font-mono text-[12px] uppercase text-neutral-700", index === 0 && section.length > 1 && "text-neutral-500")} key={item}>
                    {index === 0 && section.length > 1 ? null : <Check className="size-3.5 text-[#ff3b25]" />}
                    {item}
                  </p>
                ))}
              </div>
            ))}
          </div>
          <button
            className={cn(buttonClass, "mt-7 w-fit", !column.disabled && "border-neutral-950 bg-neutral-950 text-white hover:bg-neutral-800")}
            disabled={column.disabled}
            type="button"
          >
            {column.action}
          </button>
        </section>
      ))}
    </div>
  );
}
