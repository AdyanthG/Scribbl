"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Header } from "@/components/Header";
import { Loader2, Play, AlertCircle } from "lucide-react";

interface ProjectStatus {
    status: "queued" | "processing" | "completed" | "failed";
    step?: string;
    video_url?: string;
    error?: string;
}

export default function ProjectPage() {
    const params = useParams();
    const id = params.id as string;
    const [status, setStatus] = useState<ProjectStatus | null>(null);

    useEffect(() => {
        if (!id) return;

        const poll = async () => {
            try {
                const res = await fetch(`/api/projects/${id}/status`);
                if (res.ok) {
                    const data = await res.json();
                    setStatus(data);
                    if (data.status === "completed" || data.status === "failed") {
                        return true; // Stop polling
                    }
                }
            } catch (e) {
                console.error("Polling error", e);
            }
            return false;
        };

        const interval = setInterval(async () => {
            const stop = await poll();
            if (stop) clearInterval(interval);
        }, 2000);

        poll(); // Initial call

        return () => clearInterval(interval);
    }, [id]);

    return (
        <div className="min-h-screen flex flex-col">
            <Header />

            <main className="flex-1 flex flex-col items-center justify-center p-8">
                {!status ? (
                    <div className="flex flex-col items-center gap-4">
                        <Loader2 className="w-12 h-12 animate-spin text-primary" />
                        <p className="font-sketch text-xl">Loading project...</p>
                    </div>
                ) : status.status === "failed" ? (
                    <div className="flex flex-col items-center gap-4 text-secondary">
                        <AlertCircle className="w-16 h-16" />
                        <h2 className="font-sketch text-3xl font-bold">Oops! Something broke.</h2>
                        <p className="max-w-md text-center">{status.error}</p>
                    </div>
                ) : status.status === "completed" && status.video_url ? (
                    <div className="w-full max-w-4xl flex flex-col gap-6">
                        <div className="flex items-center justify-between">
                            <h1 className="font-sketch text-4xl font-bold">Your Sketch Video</h1>
                            <a
                                href={status.video_url}
                                download={`scribbl-${id}.mp4`}
                                className="px-4 py-2 bg-primary text-white font-sketch rounded hover:bg-primary/90 flex items-center gap-2"
                            >
                                Download Video
                            </a>
                        </div>

                        <div className="aspect-video bg-black rounded-lg overflow-hidden shadow-2xl border-4 border-foreground sketch-border">
                            <video
                                src={status.video_url}
                                controls
                                className="w-full h-full"
                                poster="/placeholder-video.png"
                            />
                        </div>
                    </div>
                ) : (
                    <div className="flex flex-col items-center gap-8 max-w-md text-center">
                        <div className="relative">
                            <div className="absolute inset-0 bg-accent/20 blur-xl rounded-full animate-pulse" />
                            <Loader2 className="w-24 h-24 animate-spin text-primary relative z-10" />
                        </div>

                        <div className="space-y-2">
                            <h2 className="font-sketch text-3xl font-bold animate-bounce">
                                Dreaming up sketches...
                            </h2>
                            <p className="text-foreground/60">
                                {status.step === "starting" && "Warming up the engine..."}
                                {status.step === "extracting" && "Reading your PDF..."}
                                {status.step === "scripting" && "Writing the script..."}
                                {status.step === "storyboard" && "Planning the visuals..."}
                                {status.step === "scenes" && "Drawing sketches & Recording voice..."}
                                {status.step === "rendering" && "Stitching the video together..."}
                            </p>
                        </div>

                        <div className="w-full bg-foreground/10 h-2 rounded-full overflow-hidden">
                            <div className="h-full bg-primary animate-progress-indeterminate" />
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}
