/**
 * レポートパイプライン用 fixture（09 §10 ケース1・ケース2 に合わせる・6軸）
 */

import type { ReportAgentInput } from '../types'

/** ケース1: 安全性高・挑戦不足型（メイン1、参加者2、サブなし）。hold/observation 高・flow 低。 */
export const inputFixtureCase1: ReportAgentInput = {
  meta: { roomId: 'room-case1' },
  averages: {
    bySection: {
      design: { mean: 4.0 },
      visibility: { mean: 4.0 },
      observation: { mean: 4.2 },
      hold: { mean: 4.2 },
      questioning: { mean: 4.2 },
      flow: { mean: 3.5 },
    },
    byRole: {
      main: {
        design: 4.0,
        visibility: 4.0,
        observation: 4.3,
        hold: 4.3,
        questioning: 4.3,
        flow: 3.4,
      },
      sub: {
        design: 0,
        visibility: 0,
        observation: 0,
        hold: 0,
        questioning: 0,
        flow: 0,
      },
      participant: {
        design: 4.0,
        visibility: 4.0,
        observation: 4.1,
        hold: 4.1,
        questioning: 4.1,
        flow: 3.6,
      },
    },
  },
  highestSection: { section: 'hold', mean: 4.2 },
  lowestSection: { section: 'flow', mean: 3.5 },
  highVarianceSections: [],
  highRoleDiffSections: [],
  sectionLabels: {
    design: { label: '高い', band: 'high' },
    visibility: { label: '高い', band: 'high' },
    observation: { label: '非常に高い', band: 'very_high' },
    hold: { label: '非常に高い', band: 'very_high' },
    questioning: { label: '非常に高い', band: 'very_high' },
    flow: { label: '改善余地', band: 'improvement' },
  },
}

/** ケース2: 説明・設計低・場の観察等高（メイン1、サブ1、参加者2） */
export const inputFixtureCase2: ReportAgentInput = {
  meta: { roomId: 'room-case2' },
  averages: {
    bySection: {
      design: { mean: 3.5 },
      visibility: { mean: 3.5 },
      observation: { mean: 4.0 },
      hold: { mean: 4.0 },
      questioning: { mean: 4.0 },
      flow: { mean: 3.7 },
    },
    byRole: {
      main: {
        design: 3.4,
        visibility: 3.4,
        observation: 4.1,
        hold: 4.1,
        questioning: 4.1,
        flow: 3.6,
      },
      sub: {
        design: 3.6,
        visibility: 3.6,
        observation: 3.9,
        hold: 3.9,
        questioning: 3.9,
        flow: 3.8,
      },
      participant: {
        design: 3.5,
        visibility: 3.5,
        observation: 4.0,
        hold: 4.0,
        questioning: 4.0,
        flow: 3.7,
      },
    },
  },
  highestSection: { section: 'observation', mean: 4.0 },
  lowestSection: { section: 'design', mean: 3.5 },
  highVarianceSections: [],
  highRoleDiffSections: [],
  sectionLabels: {
    design: { label: '改善余地', band: 'improvement' },
    visibility: { label: '改善余地', band: 'improvement' },
    observation: { label: '高い', band: 'high' },
    hold: { label: '高い', band: 'high' },
    questioning: { label: '高い', band: 'high' },
    flow: { label: '標準', band: 'standard' },
  },
}
