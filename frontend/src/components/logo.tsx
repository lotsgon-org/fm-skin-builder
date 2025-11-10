import { useTheme } from "@/components/theme-provider";
import Black from "@/icons/Black.svg?react";
import White from "@/icons/White.svg?react";

export function Logo({ className }: { className?: string }) {
  const { theme } = useTheme();

  // Determine if we're in dark mode (either explicitly dark or system preference is dark)
  const isDark =
    theme === "dark" ||
    (theme === "system" &&
      typeof window !== "undefined" &&
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches);

  const LogoComponent = isDark ? White : Black;

  return (
    <div className={className}>
      <LogoComponent width="32" height="32" />
    </div>
  );
}
