/**
 * Aggressive Inline Skating Trick Generator
 * Core logic for generating valid trick combinations
 */

class TrickGenerator {
	constructor(schema) {
		this.schema = schema;
	}

	/**
	 * Weighted random selection utility
	 * Selects a random item based on weight property
	 * @param {Array} items - Array of items with 'weight' property
	 * @returns {Object} Selected item
	 */
	weightedRandomChoice(items) {
		// Calculate total weight
		const totalWeight = items.reduce(
			(sum, item) => sum + (item.weight || 1),
			0,
		);

		// Pick a random number between 0 and totalWeight
		let random = Math.random() * totalWeight;

		// Find the item that corresponds to this random number
		for (const item of items) {
			const itemWeight = item.weight || 1;
			if (random < itemWeight) {
				return item;
			}
			random -= itemWeight;
		}

		// Fallback (shouldn't reach here)
		return items[items.length - 1];
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
			numSwitchUps = null, // null means random, otherwise specify exact number
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

		// Store numSwitchUps in trickState for later use
		if (numSwitchUps !== null) {
			trickState.numSwitchUps = numSwitchUps;
		}

		// Check if obstacle allows grinds
		if (obstacleData.allows_grinds === false) {
			return this.generateAirTrick(trickState, allowFlips);
		}

		// Build the trick sequence
		this.addApproach(trickState);
		this.addEntrySpin(trickState);
		this.addPrimaryGrind(trickState);

		// Enforce spin constraints based on grind type
		const primaryGrindData = this.schema.grinds[trickState.primaryGrind];
		if (primaryGrindData && primaryGrindData.h_block) {
			// H-block tricks: 0°, 270°, 450° only + mandatory backside/frontside
			this.enforceHBlockConstraints(trickState);
		} else if (primaryGrindData && primaryGrindData.soul_based) {
			// Soul-based tricks: multiples of 180° only (0°, 180°, 360°, 540°, etc.)
			this.enforceSoulBasedConstraints(trickState);
		}

		if (allowSwitchUps) {
			this.addSwitchUps(trickState);
		}

		// Add modifiers only for non-h-block tricks (h-block modifiers already added)
		if (!primaryGrindData || !primaryGrindData.h_block) {
			this.addModifiers(trickState);
		}

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
		const obstacleData = this.schema.obstacles[trickState.obstacle];
		const maxSpin = obstacleData.max_entry_spin || 1080;
		const spinMultiplier = obstacleData.spin_difficulty_multiplier || 1.0;

		trickState.components.push({
			type: "approach",
			value: this.schema.stances[trickState.stance].name,
		});

		// Add spin - filter by obstacle max and use weighted selection
		const spinOptions = Object.values(this.schema.entry_spins).filter(
			(spinData) => {
				return spinData.degrees > 0 && spinData.degrees <= maxSpin;
			},
		);

		if (spinOptions.length > 0) {
			const spinData = this.weightedRandomChoice(spinOptions);

			trickState.components.push({
				type: "spin",
				value: spinData.name,
			});
			trickState.difficulty += spinData.difficulty * spinMultiplier;
		}

		// Maybe add grab (weighted selection)
		if (Math.random() > 0.5) {
			const grabsArray = Object.values(this.schema.grabs);
			const grabData = this.weightedRandomChoice(grabsArray);
			trickState.components.push({
				type: "grab",
				value: grabData.name,
			});
			trickState.difficulty += grabData.difficulty;
		}

		// Maybe add flip (weighted selection)
		if (allowFlips && Math.random() > 0.7) {
			const flipsArray = Object.values(this.schema.flips);
			const flipData = this.weightedRandomChoice(flipsArray);
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
		const obstacleData = this.schema.obstacles[trickState.obstacle];
		const maxSpin = obstacleData.max_entry_spin || 540;
		const spinMultiplier = obstacleData.spin_difficulty_multiplier || 1.0;

		// 50% chance of no spin, 50% chance of spin
		if (Math.random() > 0.5) {
			// Filter spins based on obstacle constraints and convert to array
			const spinOptions = Object.values(this.schema.entry_spins).filter(
				(spinData) => {
					return spinData.degrees > 0 && spinData.degrees <= maxSpin;
				},
			);

			if (spinOptions.length > 0) {
				const spinData = this.weightedRandomChoice(spinOptions);

				trickState.components.push({
					type: "entry_spin",
					value: spinData.name,
					degrees: spinData.degrees,
				});

				// Apply obstacle-specific difficulty multiplier
				trickState.difficulty += spinData.difficulty * spinMultiplier;

				// Update direction based on spin
				if (spinData.flips_direction) {
					trickState.direction =
						trickState.direction === "forward" ? "backward" : "forward";
				}
			}
		}
	}

	addPrimaryGrind(trickState) {
		const grindsArray = Object.values(this.schema.grinds);
		const grindData = this.weightedRandomChoice(grindsArray);

		trickState.primaryGrind = grindData.id;
		trickState.components.push({
			type: "grind",
			value: grindData.name,
		});

		trickState.difficulty += grindData.difficulty;
	}

	enforceHBlockConstraints(trickState) {
		const allowedSpins = [0, 270, 450];

		// Remove entry spin if it's not allowed for h-block tricks
		const entrySpinIndex = trickState.components.findIndex(
			(c) => c.type === "entry_spin",
		);
		if (entrySpinIndex !== -1) {
			const entrySpin = trickState.components[entrySpinIndex];
			if (!allowedSpins.includes(entrySpin.degrees)) {
				// Remove invalid spin and adjust difficulty
				const spinData = Object.values(this.schema.entry_spins).find(
					(s) => s.degrees === entrySpin.degrees,
				);
				if (spinData) {
					const obstacleData = this.schema.obstacles[trickState.obstacle];
					const spinMultiplier = obstacleData.spin_difficulty_multiplier || 1.0;
					trickState.difficulty -= spinData.difficulty * spinMultiplier;
				}
				trickState.components.splice(entrySpinIndex, 1);
			}
		}

		// Force backside or frontside modifier (mandatory for h-block)
		const backsideFrontside = Object.values(this.schema.modifiers).filter(
			(mod) => mod.applies_to_h_block === true,
		);

		if (backsideFrontside.length > 0) {
			const modData = this.weightedRandomChoice(backsideFrontside);
			trickState.components.push({
				type: "modifier",
				value: modData.name,
				id: modData.id,
			});
			trickState.difficulty += modData.difficulty;
		}
	}

	enforceSoulBasedConstraints(trickState) {
		// Soul-based tricks can only have spins in multiples of 180° (0, 180, 360, 540, etc.)
		// Remove entry spin if it's not a multiple of 180°
		const entrySpinIndex = trickState.components.findIndex(
			(c) => c.type === "entry_spin",
		);
		if (entrySpinIndex !== -1) {
			const entrySpin = trickState.components[entrySpinIndex];
			if (entrySpin.degrees % 180 !== 0) {
				// Remove invalid spin (270°, 450°, etc.) and adjust difficulty
				const spinData = Object.values(this.schema.entry_spins).find(
					(s) => s.degrees === entrySpin.degrees,
				);
				if (spinData) {
					const obstacleData = this.schema.obstacles[trickState.obstacle];
					const spinMultiplier = obstacleData.spin_difficulty_multiplier || 1.0;
					trickState.difficulty -= spinData.difficulty * spinMultiplier;
				}
				trickState.components.splice(entrySpinIndex, 1);
			}
		}
	}

	addSwitchUps(trickState) {
		const obstacleData = this.schema.obstacles[trickState.obstacle];
		const lengthData =
			obstacleData.length_categories[trickState.obstacleLength];
		const maxSwitchUps = lengthData.max_switch_ups;

		if (maxSwitchUps === 0) return;

		// Use specified number or random
		let numSwitchUps;
		if (
			trickState.numSwitchUps !== undefined &&
			trickState.numSwitchUps !== null
		) {
			numSwitchUps = Math.min(trickState.numSwitchUps, maxSwitchUps);
		} else {
			numSwitchUps = Math.floor(Math.random() * (maxSwitchUps + 1));
		}

		let currentGrind = trickState.primaryGrind;
		let currentGrindData = this.schema.grinds[currentGrind];

		for (let i = 0; i < numSwitchUps; i++) {
			const validSwitchUps = currentGrindData.switch_up_to;

			if (validSwitchUps && validSwitchUps.length > 0) {
				const nextGrind = this.randomChoice(validSwitchUps);
				const nextGrindData = this.schema.grinds[nextGrind];

				trickState.components.push({
					type: "switch_up",
					value: `to ${nextGrindData.name}`,
				});

				// Base switch-up difficulty (grind difficulty + small switch cost)
				let switchUpDifficulty = nextGrindData.difficulty + 0.5;

				// Calculate positional difficulty based on foot placement
				const currentPos = currentGrindData.position_relative_to_makio;
				const nextPos = nextGrindData.position_relative_to_makio;

				if (currentPos && nextPos) {
					if (currentPos === nextPos) {
						// Same position (e.g., makio to acid - both front) = "stepping around" = very easy
						switchUpDifficulty += 0.2;
					} else if (
						(currentPos === "front" && nextPos === "back") ||
						(currentPos === "back" && nextPos === "front")
					) {
						// Front to back or back to front = cross-body movement = harder
						switchUpDifficulty += 1.0;
					} else if (currentPos === "neutral" || nextPos === "neutral") {
						// To/from neutral (makio) = moderate
						switchUpDifficulty += 0.5;
					}
				} else {
					// No positional data, use generic foot position difference
					if (currentGrindData.foot_position !== nextGrindData.foot_position) {
						switchUpDifficulty += 0.5;
					}
				}

				// Major difficulty for switching between h-block and soul-based
				if (currentGrindData.h_block !== nextGrindData.h_block) {
					switchUpDifficulty += 1.5; // Category change is significantly harder
				}

				// Check if there's a modifier (topside/negative adds complexity)
				const hasModifier = trickState.components.some(
					(c) =>
						c.type === "modifier" &&
						["topside", "negative", "true_topside", "negative_true"].includes(
							c.id,
						),
				);
				if (hasModifier) {
					// Topside = bending over obstacle, negative = underneath
					// Both make switch-ups significantly harder due to body position
					switchUpDifficulty += 0.8;

					// Cross-body switch-ups with topside/negative are particularly difficult
					if (
						(currentPos === "front" && nextPos === "back") ||
						(currentPos === "back" && nextPos === "front")
					) {
						switchUpDifficulty += 0.5; // Extra penalty for cross-body with modifier
					}
				}

				// Check if there's an exit spin on this grind (switching up while spinning)
				// This is an advanced technique - doing a switch-up mid-spin
				const hasExitSpin = trickState.components.some(
					(c) => c.type === "exit_spin" && c.degrees > 0,
				);
				if (hasExitSpin) {
					switchUpDifficulty += 1.2; // Switching up while spinning is very advanced
				}

				trickState.difficulty += switchUpDifficulty;
				currentGrind = nextGrind;
				currentGrindData = nextGrindData;
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

			// Filter valid modifiers based on grind type
			const validModifiers = Object.values(this.schema.modifiers).filter(
				(mod) => {
					// H-block tricks can ONLY have frontside/backside (no topsides/negatives)
					if (currentGrindData.h_block) {
						return mod.applies_to_h_block === true;
					}

					// Soul-based tricks can ONLY have topside/negative modifiers (not backside/frontside)
					if (currentGrindData.soul_based) {
						return mod.requires_soul_based === true;
					}

					// Frontside (neither h-block nor soul-based) can have any modifier that doesn't require soul_based or h_block
					return !mod.requires_soul_based && !mod.applies_to_h_block;
				},
			);

			if (validModifiers.length > 0) {
				const modData = this.weightedRandomChoice(validModifiers);

				trickState.components.push({
					type: "modifier",
					value: modData.name,
					id: modData.id,
				});

				trickState.difficulty += modData.difficulty;
			}
		}
	}

	addExitSpin(trickState) {
		const obstacleData = this.schema.obstacles[trickState.obstacle];
		const maxSpin = obstacleData.max_exit_spin || 540;
		const spinMultiplier = obstacleData.spin_difficulty_multiplier || 1.0;

		// Check grind type for spin restrictions
		const primaryGrindData = this.schema.grinds[trickState.primaryGrind];
		const isHBlock = primaryGrindData && primaryGrindData.h_block;
		const isSoulBased = primaryGrindData && primaryGrindData.soul_based;
		const allowedHBlockSpins = [0, 270, 450];

		// 60% chance of exit spin
		if (Math.random() > 0.4) {
			// Filter spins based on obstacle constraints and grind type restrictions
			const spinOptions = Object.values(this.schema.exit_spins).filter(
				(spinData) => {
					if (spinData.degrees === 0) return false;
					if (spinData.degrees > maxSpin) return false;

					// H-block tricks can only have 0°, 270°, 450° spins
					if (isHBlock && !allowedHBlockSpins.includes(spinData.degrees)) {
						return false;
					}

					// Soul-based tricks can only have multiples of 180° (180°, 360°, 540°, etc.)
					if (isSoulBased && spinData.degrees % 180 !== 0) {
						return false;
					}

					return true;
				},
			);

			if (spinOptions.length > 0) {
				const spinData = this.weightedRandomChoice(spinOptions);

				trickState.components.push({
					type: "exit_spin",
					value: `${spinData.name} out`,
				});

				// Apply obstacle-specific difficulty multiplier
				trickState.difficulty += spinData.difficulty * spinMultiplier;
			}
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

	findGrindByName(grindName) {
		// Find grind data by name
		return Object.values(this.schema.grinds).find(
			(grind) => grind.name === grindName,
		);
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

		// Find modifiers and grind for special topside naming
		const modifier = trickState.components.find((c) => c.type === "modifier");
		const grind = trickState.components.find((c) => c.type === "grind");
		const grindData = grind ? this.findGrindByName(grind.value) : null;

		// Handle special topside variations
		if (modifier && modifier.id === "topside" && grindData) {
			if (grindData.topside_name) {
				// Use special topside name (e.g., Fishbrain for topside makio, Sweatstance for topside mizou)
				parts.push(grindData.topside_name);
			} else {
				// Regular topside naming
				parts.push(modifier.value);
				parts.push(grind.value);
			}
		} else {
			// Regular modifier and grind naming
			if (modifier) {
				parts.push(modifier.value);
			}
			if (grind) {
				parts.push(grind.value);
			}
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
