import { Header } from "@/components/Header";
import { UploadZone } from "@/components/UploadZone";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 flex flex-col items-center justify-center p-8 pb-20">
        <div className="text-center mb-8 space-y-2">
          <h1 className="text-5xl md:text-7xl font-sketch font-bold text-primary rotate-[-1deg]">
            Learn Faster.
          </h1>
          <h2 className="text-4xl md:text-6xl font-sketch font-bold text-foreground rotate-[1deg]">
            Sketch Better.
          </h2>
        </div>

        <UploadZone />
      </main>

      <footer className="py-6 text-center text-sm text-foreground/40 font-sketch">
        Built with ❤️ by Scribbl Team
      </footer>
    </div>
  );
}
