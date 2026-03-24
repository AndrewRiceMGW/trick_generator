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

	/**
	 * Calculate shortest angular distance between two angles
	 * Normalizes to 0-180° range (we care about rotation magnitude, not direction)
	 */
	calculateAngularDistance(angle1, angle2) {
		if (angle1 === null || angle2 === null) return 0;
		
		let diff = Math.abs(angle1 - angle2);
		// Normalize to 0-180° (shortest path)
		if (diff > 180) diff = 360 - diff;
		return diff;
	}

	/**
	 * Calculate physics-based switch-up difficulty using angular rotation and edge transitions
	 */
	calculatePhysicsSwitchUpDifficulty(currentGrindData, nextGrindData, trickState) {
		// Check for topside/negative modifier
		const hasModifier = trickState.components.some(
			(c) =>
				c.type === "modifier" &&
				["topside", "negative", "true_topside", "negative_true"].includes(c.id),
		);

		// Select physics data (topside variant if applicable)
		const currentPhysics = hasModifier && currentGrindData.physics_topside
			? currentGrindData.physics_topside
			: currentGrindData.physics;
		const nextPhysics = hasModifier && nextGrindData.physics_topside
			? nextGrindData.physics_topside
			: nextGrindData.physics;

		if (!currentPhysics || !nextPhysics) {
			// Fallback to old system if physics data missing
			return 0.5;
		}

		let difficulty = 0;

		// DETECT H-BLOCK ↔ H-BLOCK TRANSITIONS (weight transfers, not rotations)
		// When h_block_type changes, feet are being lifted OFF or placed ON the h-block
		// This is vertical movement (weight transfer), not horizontal rotation
		const isHBlockTransition = currentPhysics.h_block_type !== nextPhysics.h_block_type &&
			currentPhysics.h_block_type !== "NA" && nextPhysics.h_block_type !== "NA";

		// 1. ANGULAR ROTATION - Calculate foot rotation difficulty
		const backFootRotation = this.calculateAngularDistance(
			currentPhysics.back_foot_degree,
			nextPhysics.back_foot_degree
		);
		const frontFootRotation = this.calculateAngularDistance(
			currentPhysics.front_foot_degree,
			nextPhysics.front_foot_degree
		);

		// Determine which feet are involved in h-block category change
		let backFootIsHBlockTransfer = false;
		let frontFootIsHBlockTransfer = false;
		
		if (isHBlockTransition) {
			// Check if back foot is changing h-block status
			// e.g., "both"→"back" means front foot lifted, back foot stayed
			// e.g., "back"→"both" means front foot placed down, back foot stayed
			// e.g., "both"→"front" means back foot lifted, front foot stayed
			if ((currentPhysics.h_block_type === "both" && nextPhysics.h_block_type === "front") ||
				(currentPhysics.h_block_type === "front" && nextPhysics.h_block_type === "both")) {
				backFootIsHBlockTransfer = true; // Back foot lifted/placed
			}
			if ((currentPhysics.h_block_type === "both" && nextPhysics.h_block_type === "back") ||
				(currentPhysics.h_block_type === "back" && nextPhysics.h_block_type === "both")) {
				frontFootIsHBlockTransfer = true; // Front foot lifted/placed
			}
		}

		// Apply rotation penalty only to feet that are actually rotating on the same surface
		// Feet involved in h-block transfers get minimal penalty (just weight transfer difficulty)
		let backFootPenalty = 0;
		let frontFootPenalty = 0;
		
		if (backFootIsHBlockTransfer) {
			// Back foot is lifting/placing, not rotating - minimal penalty
			backFootPenalty = 0.3;
		} else {
			// Normal rotation: 0°=0, 45°=0.3, 90°=0.8, 135°=1.3, 180°=2.0
			backFootPenalty = Math.pow(backFootRotation / 90, 1.5) * 1.0;
		}
		
		if (frontFootIsHBlockTransfer) {
			// Front foot is lifting/placing, not rotating - minimal penalty
			frontFootPenalty = 0.3;
		} else {
			// Normal rotation
			frontFootPenalty = Math.pow(frontFootRotation / 90, 1.5) * 1.0;
		}
		
		difficulty += backFootPenalty + frontFootPenalty;

		// 2. EDGE TRANSITIONS - Detect inner↔outer edge changes
		const backEdgeChanged = currentPhysics.back_foot_hblock_pointing !== "NA" &&
			nextPhysics.back_foot_hblock_pointing !== "NA" &&
			currentPhysics.back_foot_hblock_pointing !== nextPhysics.back_foot_hblock_pointing;
		const frontEdgeChanged = currentPhysics.front_foot_hblock_pointing !== "NA" &&
			nextPhysics.front_foot_hblock_pointing !== "NA" &&
			currentPhysics.front_foot_hblock_pointing !== nextPhysics.front_foot_hblock_pointing;

		if (backEdgeChanged) {
			// Edge transition adds resistance
			// Check if edge points towards other foot (harder) or away (easier)
			const pointsTowards = nextPhysics.back_foot_hblock_pointing.includes("towards");
			difficulty += pointsTowards ? 0.6 : 0.4;
		}
		if (frontEdgeChanged) {
			const pointsTowards = nextPhysics.front_foot_hblock_pointing.includes("towards");
			difficulty += pointsTowards ? 0.6 : 0.4;
		}

		// 3. KNEE DIRECTION CHANGES - Harder to reverse knee bend
		const backKneeChanged = currentPhysics.back_foot_knee !== "NA" &&
			nextPhysics.back_foot_knee !== "NA" &&
			currentPhysics.back_foot_knee !== nextPhysics.back_foot_knee &&
			currentPhysics.back_foot_knee !== "neutral" &&
			nextPhysics.back_foot_knee !== "neutral";
		const frontKneeChanged = currentPhysics.front_foot_knee !== "NA" &&
			nextPhysics.front_foot_knee !== "NA" &&
			currentPhysics.front_foot_knee !== nextPhysics.front_foot_knee &&
			currentPhysics.front_foot_knee !== "neutral" &&
			nextPhysics.front_foot_knee !== "neutral";

		if (backKneeChanged) difficulty += 0.4;
		if (frontKneeChanged) difficulty += 0.4;

		// 4. BALANCE POINT SHIFTS - Body weight distribution changes
		if (currentPhysics.balance_point !== nextPhysics.balance_point) {
			const balanceShift = `${currentPhysics.balance_point}_to_${nextPhysics.balance_point}`;
			// Cross-body balance shifts are hardest
			if (balanceShift.includes("front_to_more back") || balanceShift.includes("back_to_more front")) {
				difficulty += 0.8;
			} else if (balanceShift.includes("on top")) {
				// Transitioning to/from centered position is moderate
				difficulty += 0.3;
			} else {
				difficulty += 0.5;
			}
		}

		// 5. H-BLOCK CATEGORY CHANGES - Full penalty for true category changes
		// But NOT for soul-based grinds where h_block_type just indicates which foot is in soul position
		if (currentPhysics.h_block_type !== nextPhysics.h_block_type) {
			// Check if both are soul-based grinds (h_block: false)
			const bothSoulBased = currentGrindData.soul_based && nextGrindData.soul_based;
			
			if (bothSoulBased) {
				// Soul-based grinds: h_block_type change just means swapping which foot is in soul position
				// This is a foot role swap, not a major category change - minimal penalty
				difficulty += 0.4;
			} else {
				// True category change (h-block ↔ soul, or full h-block ↔ partial h-block)
				// This requires major foot repositioning
				difficulty += 1.2;
			}
		}

		// 6. CROSSED FOOT COMPLEXITY - Uncrossing/crossing feet is disorienting
		if (currentPhysics.crossed_foot !== nextPhysics.crossed_foot &&
			(currentPhysics.crossed_foot === "yes" || nextPhysics.crossed_foot === "yes")) {
			difficulty += 0.7;
		}

		// 7. TOPSIDE/NEGATIVE MODIFIER PENALTY
		if (hasModifier) {
			// Body position bent over/under obstacle makes all movements harder
			difficulty *= 1.3;
		}

		// 8. GRABBED TRICKS - Single-foot h-blocks are easier when grabbed
		if (nextPhysics.can_be_grabbed && nextPhysics.h_block_type !== "both") {
			difficulty *= 0.9; // 10% easier if grind can be grabbed for balance
		}

		return difficulty;
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
			// Any grind can switch to any other grind - select from all available grinds
			const allGrinds = Object.keys(this.schema.grinds).filter(
				grindId => grindId !== currentGrind // Don't switch to same grind (for now)
			);

			if (allGrinds.length > 0) {
				const nextGrind = this.randomChoice(allGrinds);
				const nextGrindData = this.schema.grinds[nextGrind];

				trickState.components.push({
					type: "switch_up",
					value: `to ${nextGrindData.name}`,
				});

				// Base switch-up difficulty (grind difficulty + small switch cost)
				let switchUpDifficulty = nextGrindData.difficulty + 0.5;

				// Add physics-based difficulty calculation
				const physicsDifficulty = this.calculatePhysicsSwitchUpDifficulty(
					currentGrindData,
					nextGrindData,
					trickState
				);
				switchUpDifficulty += physicsDifficulty;

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
