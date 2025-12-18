"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/Button";

export default function Error({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    useEffect(() => {
        console.error(error);
    }, [error]);

    return (
        <div className="flex flex-col items-center justify-center min-h-screen p-4 text-center">
            <h2 className="text-2xl font-bold text-red-500 mb-4">Something went wrong!</h2>
            <p className="text-gray-400 mb-8">{error.message}</p>
            <Button onClick={() => reset()} variant="secondary">
                Try again
            </Button>
        </div>
    );
}
