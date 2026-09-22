"use client";

import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight, Inbox, Volume2, VolumeX, Play } from "lucide-react";

export function Hero() {
  const [isMuted, setIsMuted] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (videoRef.current) {
      const playPromise = videoRef.current.play();
      if (playPromise !== undefined) {
        playPromise
          .then(() => {
            setIsPlaying(true);
          })
          .catch(() => {
            setIsPlaying(false);
          });
      }
    }
  }, []);

  const handlePlayClick = () => {
    if (videoRef.current) {
      videoRef.current.play();
      setIsPlaying(true);
    }
  };

  return (
    <section className="container mx-auto px-4 sm:px-8 py-24 md:py-32 flex flex-col items-center text-center">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-3xl space-y-8"
      >
        <div className="inline-flex items-center rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-sm font-medium text-primary">
          <Inbox className="mr-2 h-4 w-4" />
          Welcome to the future of email
        </div>
        
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-foreground">
          Your inbox, <br />
          <span className="text-primary">on autopilot.</span>
        </h1>
        
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
          Let AI understand your emails, plan the next action, and automate the routine — 
          while keeping you in control of anything important.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
          <Link href="/dashboard">
            <Button size="lg" className="h-12 px-8 text-base bg-primary text-primary-foreground hover:bg-primary/90 w-full sm:w-auto">
              Go to Dashboard
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
          <Link href="#how-it-works">
            <Button size="lg" variant="outline" className="h-12 px-8 text-base border-border hover:bg-secondary w-full sm:w-auto">
              See how it works
            </Button>
          </Link>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.2 }}
        className="mt-16 w-full max-w-5xl rounded-xl border border-border bg-card shadow-2xl overflow-hidden"
      >
        <div className="aspect-[16/9] w-full bg-black flex items-center justify-center relative group">
          <video 
            ref={videoRef}
            src="/InboxPilot%20Video.mp4" 
            loop 
            muted={isMuted} 
            playsInline 
            className={`w-full h-full object-cover transition-opacity duration-300 ${!isPlaying ? 'opacity-50' : 'opacity-100'}`}
          />
          
          {!isPlaying && (
            <button
              onClick={handlePlayClick}
              className="absolute inset-0 flex items-center justify-center z-10"
            >
              <div className="w-20 h-20 rounded-full bg-primary/90 text-primary-foreground flex items-center justify-center shadow-lg transform transition hover:scale-105">
                <Play className="w-10 h-10 ml-1" />
              </div>
            </button>
          )}

          {isPlaying && (
            <button
              onClick={() => setIsMuted(!isMuted)}
              className="absolute bottom-4 right-4 p-3 rounded-full bg-background/80 backdrop-blur-sm border border-border shadow-sm text-foreground opacity-0 group-hover:opacity-100 transition-opacity hover:bg-secondary focus:opacity-100 z-10"
              aria-label={isMuted ? "Unmute video" : "Mute video"}
            >
              {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
            </button>
          )}
        </div>
      </motion.div>
    </section>
  );
}
