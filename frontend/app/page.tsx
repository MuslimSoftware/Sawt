"use client";

import React from "react";
import { BadgeHeader } from "@/components/header/BadgeHeader";
import { CenterContent } from "@/components/body/CenterContent";
import styles from "./page.module.css";

export default function Page() {
  return (
    <main className={styles.main}>
      {/* Top fade overlay */}
      <div className={styles.topFade} />
      
      {/* Bottom fade overlay */}
      <div className={styles.bottomFade} />

      <CenterContent />
      <BadgeHeader />
    </main>
  );
}