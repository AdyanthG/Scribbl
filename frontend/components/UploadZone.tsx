"use client";

import { Upload, FileText, Sparkles, Loader2 } from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { useState } from "react";
import { useRouter } from "next/navigation";

export function UploadZone() {
    const [isDragging, setIsDragging] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const router = useRouter();

    const handleUpload = async (file: File) => {
        if (!file) return;

        setIsUploading(true);
        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch("http://localhost:8000/projects/create", {
                method: "POST",
                body: formData,
            });

            if (!res.ok) throw new Error("Upload failed");

            const data = await res.json();
            router.push(`/project/${data.project_id}`);

        } catch (error) {
            console.error("Upload error:", error);
            setIsUploading(false);
            alert("Failed to upload PDF. Please try again.");
        }
    };

    return (
        <div className="w-full max-w-2xl mx-auto mt-12">
            <motion.div
                whileHover={{ scale: 1.01, rotate: 0.5 }}
                whileTap={{ scale: 0.99 }}
                className={cn(
                    "relative group cursor-pointer",
                    "bg-white p-12 rounded-xl",
                    "border-4 border-dashed transition-colors duration-300",
                    isDragging
                        ? "border-primary bg-primary/5"
                        : "border-foreground/20 hover:border-foreground/40"
                )}
                onDragOver={(e) => {
                    e.preventDefault();
                    setIsDragging(true);
                }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={(e) => {
                    e.preventDefault();
                    setIsDragging(false);
                    const file = e.dataTransfer.files[0];
                    if (file && file.type === "application/pdf") {
                        handleUpload(file);
                    } else {
                        alert("Please upload a PDF file.");
                    }
                }}
                onClick={() => document.getElementById("file-upload")?.click()}
            >
                <input
                    id="file-upload"
                    type="file"
                    accept=".pdf"
                    className="hidden"
                    onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) handleUpload(file);
                    }}
                />

                {/* Sketchy corner accents */}
                <div className="absolute -top-2 -left-2 w-6 h-6 border-t-4 border-l-4 border-foreground rounded-tl-lg" />
                <div className="absolute -bottom-2 -right-2 w-6 h-6 border-b-4 border-r-4 border-foreground rounded-br-lg" />

                <div className="flex flex-col items-center text-center gap-4">
                    <div className="p-4 bg-accent/20 rounded-full mb-2 group-hover:scale-110 transition-transform duration-300">
                        {isUploading ? (
                            <Loader2 className="w-10 h-10 text-foreground animate-spin" />
                        ) : (
                            <Upload className="w-10 h-10 text-foreground" />
                        )}
                    </div>

                    <h2 className="text-2xl font-sketch font-bold">
                        {isUploading ? "Uploading & Processing..." : "Drop your boring PDF here"}
                    </h2>
                    <p className="text-foreground/60 max-w-md">
                        We'll turn it into a fast-paced sketch video in minutes.
                        <br />
                        <span className="text-sm text-foreground/40">
                            (Max 50MB, Text-selectable PDFs work best)
                        </span>
                    </p>

                    <button
                        disabled={isUploading}
                        className="mt-4 px-6 py-2 bg-foreground text-white font-sketch text-lg rounded-md shadow-md hover:bg-foreground/90 hover:shadow-lg transition-all -rotate-1 hover:rotate-0 disabled:opacity-50"
                    >
                        {isUploading ? "Please Wait..." : "Select File"}
                    </button>
                </div>
            </motion.div>

            {/* Feature pills */}
            <div className="flex justify-center gap-6 mt-8">
                <div className="flex items-center gap-2 text-sm font-medium text-foreground/60">
                    <FileText className="w-4 h-4" />
                    <span>Smart Summarization</span>
                </div>
                <div className="flex items-center gap-2 text-sm font-medium text-foreground/60">
                    <Sparkles className="w-4 h-4" />
                    <span>AI Sketching</span>
                </div>
            </div>
        </div>
    );
}
