/**
 * Aggressive Inline Skating Trick Generator
 * Core logic for generating valid trick combinations
 */

class TrickGenerator {
	constructor(schema) {
		this.schema = schema;
	}

	/**
	 * Generate a random trick based on mode and constraints
	 */
	generateTrick(mode = "random", options = {}) {
		const {
			obstacle = null,
			obstacleLength = "medium",
			difficultyLevel = null,
			allowSwitchUps = true,
			allowFlips = false,
		} = options;

		// Select obstacle if not provided
		const selectedObstacle =
			obstacle || this.randomChoice(Object.keys(this.schema.obstacles));
		const obstacleData = this.schema.obstacles[selectedObstacle];

		// Initialize trick state
		const trickState = {
			stance: this.randomChoice(Object.keys(this.schema.stances)),
			direction: "forward",
			obstacle: selectedObstacle,
			obstacleLength: obstacleLength,
			components: [],
			difficulty: 0,
		};

		// Check if obstacle allows grinds
		if (obstacleData.allows_grinds === false) {
			return this.generateAirTrick(trickState, allowFlips);
		}

		// Build the trick sequence
		this.addApproach(trickState);
		this.addEntrySpin(trickState);
		this.addPrimaryGrind(trickState);

		if (allowSwitchUps) {
			this.addSwitchUps(trickState);
		}

		this.addModifiers(trickState);
		this.addExitSpin(trickState);

		// Generate the trick name
		const trickName = this.generateTrickName(trickState);

		return {
			name: trickName,
			difficulty: Math.round(trickState.difficulty * 10) / 10,
			components: trickState.components,
			obstacle: selectedObstacle,
			stance: trickState.stance,
		};
	}

	/**
	 * Generate an air trick (for stairs, gaps, etc.)
	 */
	generateAirTrick(trickState, allowFlips) {
		trickState.components.push({
			type: "approach",
			value: this.schema.stances[trickState.stance].name,
		});

		// Add spin
		const spinOptions = Object.keys(this.schema.entry_spins).filter(
			(s) => s !== "0",
		);
		const spin = this.randomChoice(spinOptions);
		const spinData = this.schema.entry_spins[spin];

		trickState.components.push({
			type: "spin",
			value: spinData.name,
		});
		trickState.difficulty += spinData.difficulty;

		// Maybe add grab
		if (Math.random() > 0.5) {
			const grab = this.randomChoice(Object.keys(this.schema.grabs));
			const grabData = this.schema.grabs[grab];
			trickState.components.push({
				type: "grab",
				value: grabData.name,
			});
			trickState.difficulty += grabData.difficulty;
		}

		// Maybe add flip
		if (allowFlips && Math.random() > 0.7) {
			const flip = this.randomChoice(Object.keys(this.schema.flips));
			const flipData = this.schema.flips[flip];
			trickState.components.push({
				type: "flip",
				value: flipData.name,
			});
			trickState.difficulty += flipData.difficulty;
		}

		return {
			name: this.generateAirTrickName(trickState),
			difficulty: Math.round(trickState.difficulty * 10) / 10,
			components: trickState.components,
			obstacle: trickState.obstacle,
			stance: trickState.stance,
		};
	}

	addApproach(trickState) {
		const stanceData = this.schema.stances[trickState.stance];
		trickState.components.push({
			type: "approach",
			value: stanceData.name,
		});
		trickState.difficulty += stanceData.difficulty;
	}

	addEntrySpin(trickState) {
		// 50% chance of no spin, 50% chance of spin
		if (Math.random() > 0.5) {
			const spinOptions = Object.keys(this.schema.entry_spins).filter(
				(s) => s !== "0",
			);
			const spin = this.randomChoice(spinOptions);
			const spinData = this.schema.entry_spins[spin];

			trickState.components.push({
				type: "entry_spin",
				value: spinData.name,
				degrees: spinData.degrees,
			});

			trickState.difficulty += spinData.difficulty;

			// Update direction based on spin
			if (spinData.flips_direction) {
				trickState.direction =
					trickState.direction === "forward" ? "backward" : "forward";
			}
		}
	}

	addPrimaryGrind(trickState) {
		const grindId = this.randomChoice(Object.keys(this.schema.grinds));
		const grindData = this.schema.grinds[grindId];

		trickState.primaryGrind = grindId;
		trickState.components.push({
			type: "grind",
			value: grindData.name,
		});

		trickState.difficulty += grindData.difficulty;
	}

	addSwitchUps(trickState) {
		const obstacleData = this.schema.obstacles[trickState.obstacle];
		const lengthData =
			obstacleData.length_categories[trickState.obstacleLength];
		const maxSwitchUps = lengthData.max_switch_ups;

		if (maxSwitchUps === 0) return;

		// Random number of switch-ups (0 to max)
		const numSwitchUps = Math.floor(Math.random() * (maxSwitchUps + 1));

		let currentGrind = trickState.primaryGrind;

		for (let i = 0; i < numSwitchUps; i++) {
			const currentGrindData = this.schema.grinds[currentGrind];
			const validSwitchUps = currentGrindData.switch_up_to;

			if (validSwitchUps && validSwitchUps.length > 0) {
				const nextGrind = this.randomChoice(validSwitchUps);
				const nextGrindData = this.schema.grinds[nextGrind];

				trickState.components.push({
					type: "switch_up",
					value: `to ${nextGrindData.name}`,
				});

				trickState.difficulty += nextGrindData.difficulty + 1; // +1 for switch-up difficulty
				currentGrind = nextGrind;
			}
		}

		trickState.difficulty *= lengthData.difficulty_multiplier;
	}

	addModifiers(trickState) {
		// 30% chance of adding a modifier
		if (Math.random() > 0.7) {
			const currentGrind = this.findCurrentGrind(trickState);
			if (!currentGrind) return;

			const currentGrindData = this.schema.grinds[currentGrind];

			// Filter valid modifiers
			const validModifiers = Object.keys(this.schema.modifiers).filter(
				(modId) => {
					const mod = this.schema.modifiers[modId];
					if (mod.requires_soul_based && !currentGrindData.soul_based) {
						return false;
					}
					return true;
				},
			);

			if (validModifiers.length > 0) {
				const modId = this.randomChoice(validModifiers);
				const modData = this.schema.modifiers[modId];

				trickState.components.push({
					type: "modifier",
					value: modData.name,
				});

				trickState.difficulty += modData.difficulty;
			}
		}
	}

	addExitSpin(trickState) {
		// 60% chance of exit spin
		if (Math.random() > 0.4) {
			const spinOptions = Object.keys(this.schema.exit_spins).filter(
				(s) => s !== "0",
			);
			const spin = this.randomChoice(spinOptions);
			const spinData = this.schema.exit_spins[spin];

			trickState.components.push({
				type: "exit_spin",
				value: `${spinData.name} out`,
			});

			trickState.difficulty += spinData.difficulty;
		}
	}

	findCurrentGrind(trickState) {
		// Find the last grind in components (could be primary or switch-up target)
		for (let i = trickState.components.length - 1; i >= 0; i--) {
			if (trickState.components[i].type === "grind") {
				// Find grind ID by name
				return Object.keys(this.schema.grinds).find(
					(id) =>
						this.schema.grinds[id].name === trickState.components[i].value,
				);
			}
			if (trickState.components[i].type === "switch_up") {
				// Extract grind name from "to [grind]"
				const grindName = trickState.components[i].value.replace("to ", "");
				return Object.keys(this.schema.grinds).find(
					(id) => this.schema.grinds[id].name === grindName,
				);
			}
		}
		return trickState.primaryGrind;
	}

	generateTrickName(trickState) {
		const parts = [];

		// Find entry spin
		const entrySpin = trickState.components.find(
			(c) => c.type === "entry_spin",
		);
		const exitSpin = trickState.components.find((c) => c.type === "exit_spin");

		// Handle special naming (Cab, Half Cab, etc.)
		if (trickState.stance === "fakie" && entrySpin) {
			if (entrySpin.degrees === 360) {
				parts.push("Cab");
			} else if (entrySpin.degrees === 180) {
				parts.push("Half Cab");
			} else {
				parts.push(`Fakie ${entrySpin.value}`);
			}
		} else if (trickState.stance === "switch") {
			if (entrySpin) {
				parts.push(`Switch ${entrySpin.value}`);
			} else {
				parts.push("Switch");
			}
		} else if (entrySpin) {
			parts.push(entrySpin.value);
		}

		// Find modifiers
		const modifier = trickState.components.find((c) => c.type === "modifier");
		if (modifier) {
			parts.push(modifier.value);
		}

		// Find primary grind
		const grind = trickState.components.find((c) => c.type === "grind");
		if (grind) {
			parts.push(grind.value);
		}

		// Find switch-ups
		const switchUps = trickState.components.filter(
			(c) => c.type === "switch_up",
		);
		switchUps.forEach((su) => {
			parts.push(su.value);
		});

		// Add exit spin
		if (exitSpin) {
			parts.push(exitSpin.value);
		}

		return parts.join(" ");
	}

	generateAirTrickName(trickState) {
		const parts = [];

		// Get all components
		const spin = trickState.components.find((c) => c.type === "spin");
		const grab = trickState.components.find((c) => c.type === "grab");
		const flip = trickState.components.find((c) => c.type === "flip");

		// Handle stance
		if (trickState.stance === "fakie") {
			parts.push("Fakie");
		} else if (trickState.stance === "switch") {
			parts.push("Switch");
		}

		// Add spin
		if (spin) {
			parts.push(spin.value);
		}

		// Add grab
		if (grab) {
			parts.push(grab.value);
		}

		// Add flip
		if (flip) {
			parts.push(flip.value);
		}

		return parts.join(" ") || "Straight Air";
	}

	/**
	 * Generate multiple tricks at once
	 */
	generateMultipleTricks(count, mode, options) {
		const tricks = [];
		for (let i = 0; i < count; i++) {
			tricks.push(this.generateTrick(mode, options));
		}
		return tricks;
	}

	/**
	 * Filter tricks by difficulty level
	 */
	filterByDifficulty(tricks, level) {
		const levelData = this.schema.difficulty_levels[level];
		if (!levelData) return tricks;

		return tricks.filter(
			(trick) =>
				trick.difficulty >= levelData.min && trick.difficulty <= levelData.max,
		);
	}

	/**
	 * Utility: Get random choice from array
	 */
	randomChoice(array) {
		return array[Math.floor(Math.random() * array.length)];
	}
}

// Export for use in HTML
if (typeof module !== "undefined" && module.exports) {
	module.exports = TrickGenerator;
}
