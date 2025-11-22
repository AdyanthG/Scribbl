import { Pencil } from "lucide-react";
import Link from "next/link";

export function Header() {
    return (
        <header className="w-full p-6 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
                <div className="w-10 h-10 bg-foreground text-white rounded-lg flex items-center justify-center transform -rotate-3">
                    <Pencil className="w-6 h-6" />
                </div>
                <h1 className="text-2xl font-sketch font-bold tracking-tight">
                    Scribbl
                </h1>
            </Link>

            <nav className="flex items-center gap-4">
                <Link
                    href="/my-sketches"
                    className="font-sketch text-lg hover:underline decoration-wavy decoration-primary"
                >
                    My Sketches
                </Link>
            </nav>
        </header>
    );
}
