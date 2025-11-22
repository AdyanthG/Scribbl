"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { Loader2, Trash2, Play, Calendar } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

interface Project {
    id: string;
    status: string;
    video_url?: string;
    step?: string;
    created_at?: string; // Not yet implemented in backend, but good to have
}

export default function MySketchesPage() {
    const [projects, setProjects] = useState<Project[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const mySketches = JSON.parse(localStorage.getItem("my_sketches") || "[]");

        if (mySketches.length === 0) {
            setProjects([]);
            setLoading(false);
            return;
        }

        const idsParam = mySketches.join(",");
        fetch(`/api/projects/list?ids=${idsParam}`)
            .then((res) => res.json())
            .then((data) => {
                setProjects(data);
                setLoading(false);
            })
            .catch((err) => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    return (
        <div className="min-h-screen flex flex-col bg-background">
            <Header />

            <main className="flex-1 p-8 max-w-6xl mx-auto w-full">
                <div className="flex items-center justify-between mb-8">
                    <h1 className="text-4xl font-sketch font-bold">My Sketches</h1>
                    <div className="text-sm text-foreground/60 font-medium">
                        {projects.length} {projects.length === 1 ? "Sketch" : "Sketches"}
                    </div>
                </div>

                {loading ? (
                    <div className="flex justify-center py-20">
                        <Loader2 className="w-10 h-10 animate-spin text-primary" />
                    </div>
                ) : projects.length === 0 ? (
                    <div className="text-center py-20 opacity-60">
                        <p className="font-sketch text-2xl mb-4">No sketches yet!</p>
                        <Link
                            href="/"
                            className="px-6 py-2 bg-foreground text-white font-sketch rounded hover:bg-foreground/90"
                        >
                            Create your first one
                        </Link>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {projects.map((project) => (
                            <motion.div
                                key={project.id}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="group relative bg-white rounded-xl border-2 border-foreground/10 overflow-hidden hover:border-primary/50 transition-colors shadow-sm hover:shadow-md"
                            >
                                {/* Thumbnail Area */}
                                <div className="aspect-video bg-accent/10 flex items-center justify-center relative overflow-hidden">
                                    {project.status === "completed" && project.video_url ? (
                                        <video
                                            src={project.video_url}
                                            className="w-full h-full object-cover"
                                            muted
                                            onMouseOver={(e) => e.currentTarget.play()}
                                            onMouseOut={(e) => {
                                                e.currentTarget.pause();
                                                e.currentTarget.currentTime = 0;
                                            }}
                                        />
                                    ) : (
                                        <div className="flex flex-col items-center gap-2 text-foreground/40">
                                            <Loader2 className="w-8 h-8 animate-spin" />
                                            <span className="font-sketch text-sm">Processing...</span>
                                        </div>
                                    )}

                                    {/* Overlay Play Button */}
                                    {project.status === "completed" && (
                                        <div className="absolute inset-0 flex items-center justify-center bg-black/10 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center shadow-lg">
                                                <Play className="w-5 h-5 fill-foreground text-foreground ml-1" />
                                            </div>
                                        </div>
                                    )}
                                </div>

                                {/* Info Area */}
                                <div className="p-4">
                                    <div className="flex items-start justify-between gap-2">
                                        <Link href={`/project/${project.id}`} className="flex-1">
                                            <h3 className="font-sketch font-bold text-lg truncate hover:text-primary transition-colors">
                                                {project.id.slice(0, 8)}...
                                            </h3>
                                            <div className="flex items-center gap-2 text-xs text-foreground/50 mt-1">
                                                <Calendar className="w-3 h-3" />
                                                <span>Just now</span>
                                            </div>
                                        </Link>

                                        <button
                                            className="text-foreground/20 hover:text-red-500 transition-colors p-1"
                                            onClick={(e) => {
                                                e.preventDefault();
                                                // TODO: Implement delete
                                                alert("Delete coming soon!");
                                            }}
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>

                                    {/* Status Badge */}
                                    <div className="mt-4 flex items-center gap-2">
                                        <div className={`w-2 h-2 rounded-full ${project.status === "completed" ? "bg-green-500" :
                                            project.status === "failed" ? "bg-red-500" : "bg-yellow-500 animate-pulse"
                                            }`} />
                                        <span className="text-xs font-medium uppercase tracking-wider text-foreground/60">
                                            {project.status}
                                        </span>
                                    </div>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
}
