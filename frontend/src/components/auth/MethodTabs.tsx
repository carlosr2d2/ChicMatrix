"use client";

import { Tab, TabGroup, TabList, TabPanel, TabPanels } from "@headlessui/react";

type MethodTabsProps = {
  tabs: { id: string; label: string }[];
  children: React.ReactNode[];
};

export function MethodTabs({ tabs, children }: MethodTabsProps) {
  return (
    <TabGroup>
      <TabList className="grid grid-cols-3 gap-2 rounded-sm bg-white p-1 border border-sand/80 mb-8">
        {tabs.map((tab) => (
          <Tab
            key={tab.id}
            className="rounded-sm px-3 py-2.5 text-xs sm:text-sm font-medium tracking-wide uppercase transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ink data-[selected]:bg-ink data-[selected]:text-white data-[hover]:text-ink data-[selected]:data-[hover]:text-white text-stone-500"
          >
            {tab.label}
          </Tab>
        ))}
      </TabList>
      <TabPanels>
        {children.map((panel, index) => (
          <TabPanel key={tabs[index]?.id ?? index} className="focus:outline-none animate-fade-in">
            {panel}
          </TabPanel>
        ))}
      </TabPanels>
    </TabGroup>
  );
}
