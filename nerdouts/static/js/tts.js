/**
 * Browser-based Text-to-Speech module for workout announcements
 * Provides a cross-browser compatible TTS solution with fallback handling
 */

class WorkoutTTS {
    constructor() {
        this.isSupported = this.checkSupport();
        this.voices = [];
        this.selectedVoice = null;
        this.isSpeaking = false;
        this.queue = [];
        
        // Default settings
        this.settings = {
            rate: 1.0,      // Speaking rate (0.1 - 10)
            pitch: 1.0,     // Voice pitch (0 - 2)
            volume: 1.0,    // Volume (0 - 1)
            lang: 'en-US'   // Language
        };
        
        if (this.isSupported) {
            this.init();
        }
    }
    
    /**
     * Check if Web Speech API is supported
     */
    checkSupport() {
        return 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window;
    }
    
    /**
     * Initialize TTS and load available voices
     */
    init() {
        // Handle speech events first
        this.setupEventHandlers();
        
        // Chrome loads voices asynchronously
        if (speechSynthesis.onvoiceschanged !== undefined) {
            speechSynthesis.onvoiceschanged = () => {
                console.log('TTS: onvoiceschanged event fired');
                this.loadVoices();
                // Notify listeners that voices have loaded
                if (this.onVoicesLoaded) {
                    this.onVoicesLoaded(this.voices);
                }
            };
        }
        
        // Try loading voices immediately
        this.loadVoices();
        
        // Chrome hack: Sometimes needs a speech to trigger voice loading
        if (this.voices.length === 0) {
            console.log('TTS: No voices found, attempting Chrome workaround...');
            // Create a silent utterance to trigger voice loading
            const silentUtterance = new SpeechSynthesisUtterance('');
            silentUtterance.volume = 0;
            speechSynthesis.speak(silentUtterance);
            speechSynthesis.cancel(); // Cancel immediately
            
            // Try loading again after a moment
            setTimeout(() => this.loadVoices(), 100);
        }
    }
    
    /**
     * Load available voices
     */
    loadVoices() {
        try {
            this.voices = speechSynthesis.getVoices();
            
            // Try to select a good default voice
            if (this.voices.length > 0 && !this.selectedVoice) {
                // Prefer local voices for better performance
                const localVoices = this.voices.filter(voice => voice.localService);
                const englishVoices = this.voices.filter(voice => voice.lang.startsWith('en'));
                
                // Priority: Local English > Any English > First available
                this.selectedVoice = localVoices.find(voice => voice.lang.startsWith('en')) ||
                                    englishVoices[0] ||
                                    this.voices[0];
            }
            
            console.log(`TTS: Loaded ${this.voices.length} voices`);
        } catch (error) {
            console.error('TTS: Error loading voices:', error);
            this.voices = [];
        }
    }
    
    /**
     * Setup global event handlers for speech synthesis
     */
    setupEventHandlers() {
        // Monitor speaking state
        speechSynthesis.addEventListener('start', () => {
            this.isSpeaking = true;
        });
        
        speechSynthesis.addEventListener('end', () => {
            this.isSpeaking = false;
            this.processQueue();
        });
    }
    
    /**
     * Speak text with optional settings override
     * @param {string} text - Text to speak
     * @param {Object} options - Optional settings override
     * @returns {Promise} - Resolves when speech completes
     */
    speak(text, options = {}) {
        return new Promise((resolve, reject) => {
            if (!this.isSupported) {
                console.warn('TTS: Speech synthesis not supported');
                reject(new Error('Speech synthesis not supported'));
                return;
            }
            
            // Create utterance
            const utterance = new SpeechSynthesisUtterance(text);
            
            // Apply settings
            const settings = { ...this.settings, ...options };
            utterance.rate = settings.rate;
            utterance.pitch = settings.pitch;
            utterance.volume = settings.volume;
            utterance.lang = settings.lang;
            
            // Set voice if available
            if (this.selectedVoice) {
                utterance.voice = this.selectedVoice;
            }
            
            // Handle completion
            utterance.onend = () => {
                this.isSpeaking = false;
                resolve();
            };
            
            utterance.onerror = (event) => {
                this.isSpeaking = false;
                console.error('TTS: Speech error', event);
                reject(event);
            };
            
            // Add to queue if already speaking
            if (this.isSpeaking || speechSynthesis.pending) {
                this.queue.push({ utterance, resolve, reject });
            } else {
                // Speak immediately
                this.isSpeaking = true;
                speechSynthesis.speak(utterance);
            }
        });
    }
    
    /**
     * Process queued utterances
     */
    processQueue() {
        if (this.queue.length > 0 && !this.isSpeaking) {
            const { utterance, resolve, reject } = this.queue.shift();
            
            utterance.onend = () => {
                this.isSpeaking = false;
                resolve();
                this.processQueue();
            };
            
            utterance.onerror = (event) => {
                this.isSpeaking = false;
                reject(event);
                this.processQueue();
            };
            
            this.isSpeaking = true;
            speechSynthesis.speak(utterance);
        }
    }
    
    /**
     * Stop all speech immediately
     */
    stop() {
        if (this.isSupported) {
            speechSynthesis.cancel();
            this.queue = [];
            this.isSpeaking = false;
        }
    }
    
    /**
     * Pause current speech
     */
    pause() {
        if (this.isSupported && speechSynthesis.speaking) {
            speechSynthesis.pause();
        }
    }
    
    /**
     * Resume paused speech
     */
    resume() {
        if (this.isSupported && speechSynthesis.paused) {
            speechSynthesis.resume();
        }
    }
    
    /**
     * Update TTS settings
     * @param {Object} newSettings - Settings to update
     */
    updateSettings(newSettings) {
        this.settings = { ...this.settings, ...newSettings };
    }
    
    /**
     * Set a specific voice by name or index
     * @param {string|number} voiceIdentifier - Voice name or index
     */
    setVoice(voiceIdentifier) {
        if (typeof voiceIdentifier === 'number') {
            this.selectedVoice = this.voices[voiceIdentifier] || null;
        } else {
            this.selectedVoice = this.voices.find(voice => 
                voice.name === voiceIdentifier
            ) || null;
        }
    }
    
    /**
     * Get list of available voices
     * @returns {Array} Available voices
     */
    getVoices() {
        return this.voices.map((voice, index) => ({
            index,
            name: voice.name,
            lang: voice.lang,
            localService: voice.localService,
            default: voice.default
        }));
    }
    
    /**
     * Test TTS with a sample phrase
     */
    test() {
        this.speak('Text to speech is working correctly');
    }
}

// Export for use in other modules
window.WorkoutTTS = WorkoutTTS;