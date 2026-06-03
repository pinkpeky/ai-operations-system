"""Commercial operations API routes."""

from __future__ import annotations

import html
import asyncio
import logging
import re
from typing import Any
from datetime import datetime, timezone
from urllib.parse import parse_qs, unquote, urlparse
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.rag import build_retrieved_chunk_from_reranked, create_hybrid_search_pipeline
from app.commercial_operations.service import CommercialOperationService
from app.commercial_operations.video_agent import CommercialVideoAgent
from app.commercial_operations.video_orchestrator import CommercialVideoMainAgent
from app.core.config import get_settings
from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.digital_humans import DigitalHumanService
from app.reranker.reranker_client import RerankerClient
from app.schemas.commercial_operation import (
    CommercialOperationApprovalCreateRequest,
    CommercialOperationApprovalDecisionRequest,
    CommercialOperationApprovalListResponse,
    CommercialOperationApprovalResponse,
    CommercialOperationAssetRequestCreateRequest,
    CommercialOperationAssetRequestDecisionRequest,
    CommercialOperationAssetRequestGenerateRequest,
    CommercialOperationAssetRequestListResponse,
    CommercialOperationAssetRequestResponse,
    CommercialOperationAssetRequestUpdateRequest,
    CommercialOperationComfyUIAdapterConfigCreateRequest,
    CommercialOperationComfyUIAdapterConfigDecisionRequest,
    CommercialOperationComfyUIAdapterConfigListResponse,
    CommercialOperationComfyUIAdapterConfigResponse,
    CommercialOperationComfyUIAdapterConfigUpdateRequest,
    CommercialOperationComfyUIAdapterDispatchCreateRequest,
    CommercialOperationComfyUIAdapterDispatchDecisionRequest,
    CommercialOperationComfyUIAdapterDispatchListResponse,
    CommercialOperationComfyUIAdapterDispatchResponse,
    CommercialOperationComfyUIRuntimeSubmitRequest,
    CommercialOperationComfyUIAdapterDispatchUpdateRequest,
    CommercialOperationComfyUIConnectionProbeCreateRequest,
    CommercialOperationComfyUIConnectionProbeDecisionRequest,
    CommercialOperationComfyUIConnectionProbeListResponse,
    CommercialOperationComfyUIConnectionProbeResponse,
    CommercialOperationComfyUIConnectionProbeUpdateRequest,
    CommercialOperationComfyUIExecutionPlanCreateRequest,
    CommercialOperationComfyUIExecutionPlanDecisionRequest,
    CommercialOperationComfyUIExecutionPlanListResponse,
    CommercialOperationComfyUIExecutionPlanResponse,
    CommercialOperationComfyUIExecutionPlanUpdateRequest,
    CommercialOperationComfyUIHandoffCreateRequest,
    CommercialOperationComfyUIHandoffDecisionRequest,
    CommercialOperationComfyUIHandoffListResponse,
    CommercialOperationComfyUIHandoffResponse,
    CommercialOperationComfyUIHandoffUpdateRequest,
    CommercialOperationComfyUIJobRequestCreateRequest,
    CommercialOperationComfyUIJobRequestDecisionRequest,
    CommercialOperationComfyUIJobRequestListResponse,
    CommercialOperationComfyUIJobRequestResponse,
    CommercialOperationComfyUIJobRequestUpdateRequest,
    CommercialOperationComfyUIPreflightCreateRequest,
    CommercialOperationComfyUIPreflightDecisionRequest,
    CommercialOperationComfyUIPreflightListResponse,
    CommercialOperationComfyUIPreflightResponse,
    CommercialOperationComfyUIPreflightUpdateRequest,
    CommercialOperationComfyUIRuntimeGateCreateRequest,
    CommercialOperationComfyUIRuntimeGateDecisionRequest,
    CommercialOperationComfyUIRuntimeGateListResponse,
    CommercialOperationComfyUIRuntimeGateResponse,
    CommercialOperationComfyUIRuntimeGateUpdateRequest,
    CommercialOperationComfyUIRuntimeDryRunCreateRequest,
    CommercialOperationComfyUIRuntimeDryRunDecisionRequest,
    CommercialOperationComfyUIRuntimeDryRunListResponse,
    CommercialOperationComfyUIRuntimeDryRunResponse,
    CommercialOperationComfyUIRuntimeDryRunUpdateRequest,
    CommercialOperationComfyUIRuntimeActivationCreateRequest,
    CommercialOperationComfyUIRuntimeActivationDecisionRequest,
    CommercialOperationComfyUIRuntimeActivationListResponse,
    CommercialOperationComfyUIRuntimeActivationResponse,
    CommercialOperationComfyUIRuntimeActivationUpdateRequest,
    CommercialOperationContentDraftCreateRequest,
    CommercialOperationContentDraftDecisionRequest,
    CommercialOperationContentDraftGenerateRequest,
    CommercialOperationContentDraftListResponse,
    CommercialOperationContentDraftResponse,
    CommercialOperationContentDraftUpdateRequest,
    CommercialOperationCreateRequest,
    CommercialOperationDeliverableCreateRequest,
    CommercialOperationDeliverableDecisionRequest,
    CommercialOperationDeliverableListResponse,
    CommercialOperationDeliverableResponse,
    CommercialOperationDeliverableUpdateRequest,
    CommercialOperationDigitalHumanDeliveryLinkRequest,
    CommercialOperationDigitalHumanDeliveryLinkResponse,
    CommercialOperationDryRunCreateRequest,
    CommercialOperationDryRunDecisionRequest,
    CommercialOperationDryRunListResponse,
    CommercialOperationDryRunResponse,
    CommercialOperationEvidenceSnapshotCreateRequest,
    CommercialOperationEvidenceSnapshotDecisionRequest,
    CommercialOperationEvidenceSnapshotGenerateRequest,
    CommercialOperationEvidenceSnapshotListResponse,
    CommercialOperationEvidenceSnapshotResponse,
    CommercialOperationEvidenceSnapshotUpdateRequest,
    CommercialOperationExecutionRequestCreateRequest,
    CommercialOperationExecutionRequestDecisionRequest,
    CommercialOperationExecutionRequestListResponse,
    CommercialOperationExecutionRequestResponse,
    CommercialOperationExecutionRequestUpdateRequest,
    CommercialOperationExecutionRunCreateRequest,
    CommercialOperationExecutionRunDecisionRequest,
    CommercialOperationExecutionRunListResponse,
    CommercialOperationExecutionRunResponse,
    CommercialOperationExecutionRunUpdateRequest,
    CommercialOperationAgentSkillOrchestrationResponse,
    CommercialOperationMainAgentAdvanceRequest,
    CommercialOperationMainAgentAdvanceResponse,
    CommercialOperationLinkCreateRequest,
    CommercialOperationLinkListResponse,
    CommercialOperationLinkResponse,
    CommercialOperationListResponse,
    CommercialOperationLoopSummaryResponse,
    CommercialOperationMonitoringObservationCreateRequest,
    CommercialOperationMonitoringObservationDecisionRequest,
    CommercialOperationMonitoringObservationListResponse,
    CommercialOperationMonitoringObservationResponse,
    CommercialOperationMonitoringObservationUpdateRequest,
    CommercialOperationOptimizationDecisionCreateRequest,
    CommercialOperationOptimizationDecisionDecisionRequest,
    CommercialOperationOptimizationDecisionListResponse,
    CommercialOperationOptimizationDecisionResponse,
    CommercialOperationOptimizationDecisionUpdateRequest,
    CommercialOperationOutputCandidateCreateRequest,
    CommercialOperationOutputCandidateListResponse,
    CommercialOperationOutputCandidateResponse,
    CommercialOperationOutputPrepPackageResponse,
    CommercialOperationFinalSelectionCreateRequest,
    CommercialOperationFinalSelectionListResponse,
    CommercialOperationFinalSelectionResponse,
    CommercialOperationPlanCreateRequest,
    CommercialOperationPlanListResponse,
    CommercialOperationPlanPreviewResponse,
    CommercialOperationPlanResponse,
    CommercialOperationPlatformMetricSnapshotCreateRequest,
    CommercialOperationPlatformMetricSnapshotListResponse,
    CommercialOperationPlatformMetricSnapshotResponse,
    CommercialOperationMetricAnalysisScheduleRequest,
    CommercialOperationMetricAnalysisScheduleResponse,
    CommercialOperationMetricAnalysisDispatchQueueResponse,
    CommercialOperationMetricAnalysisRunRequest,
    CommercialOperationMetricAnalysisRunResponse,
    CommercialOperationMetricDispatchClaimListResponse,
    CommercialOperationMetricDispatchClaimRequest,
    CommercialOperationMetricDispatchClaimResponse,
    CommercialOperationMetricDispatchClaimStatusRequest,
    CommercialOperationMetricDispatchCustomerPollRequest,
    CommercialOperationMetricDispatchCustomerPollResponse,
    CommercialOperationMetricDispatchPollSchedulerRequest,
    CommercialOperationMetricDispatchPollSchedulerResponse,
    CommercialOperationMetricPullbackHandoffResponse,
    CommercialOperationMetricPullbackAdapterProfileResponse,
    CommercialOperationMetricPullbackBrowserAssistSessionRequest,
    CommercialOperationMetricPullbackBrowserAssistSessionResponse,
    CommercialOperationMetricPullbackExportImportPreviewRequest,
    CommercialOperationMetricPullbackExportImportPreviewResponse,
    CommercialOperationMetricPullbackResultRequest,
    CommercialOperationMetricPullbackResultResponse,
    CommercialOperationProductionClosedLoopActionAuditCreateRequest,
    CommercialOperationProductionClosedLoopActionAuditListResponse,
    CommercialOperationProductionClosedLoopActionAuditRecordResponse,
    CommercialOperationProductionClosedLoopActionReadinessRefreshRequest,
    CommercialOperationProductionClosedLoopActionReadinessRefreshResponse,
    CommercialOperationProductionClosedLoopActionResultRecordValidationRequest,
    CommercialOperationProductionClosedLoopActionResultRecordValidationResponse,
    CommercialOperationProductionClosedLoopActionResultBindingRequest,
    CommercialOperationProductionClosedLoopActionResultBindingResponse,
    CommercialOperationProductionClosedLoopInterventionQueueItemResponse,
    CommercialOperationProductionClosedLoopInterventionQueueResponse,
    CommercialOperationProductionClosedLoopInterventionAcknowledgementListResponse,
    CommercialOperationProductionClosedLoopInterventionAcknowledgementRequest,
    CommercialOperationProductionClosedLoopInterventionAcknowledgementResponse,
    CommercialOperationProductionClosedLoopInterventionReminderDispatchListResponse,
    CommercialOperationProductionClosedLoopInterventionReminderDispatchRequest,
    CommercialOperationProductionClosedLoopInterventionReminderDispatchResponse,
    CommercialOperationProductionClosedLoopAcceptanceSummaryResponse,
    CommercialOperationProductionClosedLoopDeliveryAuditBlockerClearancePlanResponse,
    CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceListResponse,
    CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceRecordResponse,
    CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceRequest,
    CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverageResponse,
    CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceReadinessRefreshRequest,
    CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceReadinessRefreshResponse,
    CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookPackageListResponse,
    CommercialOperationProductionClosedLoopDeliveryAuditBlockerWorkOrderAssignmentRequest,
    CommercialOperationProductionClosedLoopDeliveryAuditBlockerWorkOrderAssignmentResponse,
    CommercialOperationProductionClosedLoopDeliveryAuditNextActionPlanResponse,
    CommercialOperationProductionClosedLoopDeliveryAuditOpenClawProviderHandoffResponse,
    CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecordListResponse,
    CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecordRequest,
    CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecordResponse,
    CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueResponse,
    CommercialOperationProductionClosedLoopDeliveryActionPackageListResponse,
    CommercialOperationProductionClosedLoopDeliveryActionEvidenceListResponse,
    CommercialOperationProductionClosedLoopDeliveryActionEvidenceRecordResponse,
    CommercialOperationProductionClosedLoopDeliveryActionEvidenceRequest,
    CommercialOperationProductionClosedLoopDeliveryRemediationMapResponse,
    CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderListResponse,
    CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderAssignmentRequest,
    CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderAssignmentResponse,
    CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCompletionRequest,
    CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCompletionResponse,
    CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverageResponse,
    CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrepResponse,
    CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderReadinessRefreshRequest,
    CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderReadinessRefreshResponse,
    CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRecordResponse,
    CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRequest,
    CommercialOperationProductionClosedLoopDeliveryPlanResponse,
    CommercialOperationNextCycleDraftRequest,
    CommercialOperationNextCycleDraftResponse,
    CommercialOperationProductionClosedLoopNextActionResponse,
    CommercialOperationProductionClosedLoopReadinessResponse,
    CommercialOperationProductionTaskCreateRequest,
    CommercialOperationProductionTaskListResponse,
    CommercialOperationProductionTaskResponse,
    CommercialOperationProjectDecisionRequest,
    CommercialOperationProjectMaterialCreateRequest,
    CommercialOperationProjectMaterialListResponse,
    CommercialOperationProjectMaterialResponse,
    CommercialOperationPublishPackageCreateRequest,
    CommercialOperationPublishPackageListResponse,
    CommercialOperationPublishExecutionHandoffResponse,
    CommercialOperationPublishExecutionResultCreateRequest,
    CommercialOperationPublishExecutionResultResponse,
    CommercialOperationPublishExecutionStatusResponse,
    CommercialOperationPublishExecutionStatusUpdateRequest,
    CommercialOperationPublishPrepPackageResponse,
    CommercialOperationPublishPackageResponse,
    CommercialOperationResultCreateRequest,
    CommercialOperationResultDecisionRequest,
    CommercialOperationResultListResponse,
    CommercialOperationResultResponse,
    CommercialOperationResultUpdateRequest,
    CommercialOperationResponse,
    CommercialOperationUpdateRequest,
    CommercialOperationVideoAgentOrchestrationRequest,
    CommercialOperationVideoAgentOrchestrationResponse,
    CommercialOperationWorkflowCandidateListResponse,
    CommercialOperationWorkflowSelectionCreateRequest,
    CommercialOperationWorkflowSelectionListResponse,
    CommercialOperationWorkflowSelectionResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/commercial-operations", tags=["commercial-operations"])


class CommercialOperationPlanningIntelligenceRequest(BaseModel):
    """Request for external planning intelligence before LLM plan generation."""

    topic: str = Field(..., min_length=1, max_length=500)
    platform: str | None = Field(default=None, max_length=100)
    project_title: str | None = Field(default=None, max_length=255)
    objective: str | None = Field(default=None, max_length=1000)
    target_audience: str | None = Field(default=None, max_length=500)
    max_results: int = Field(default=8, ge=1, le=20)


class CommercialOperationPlanningIntelligenceResponse(BaseModel):
    """External intelligence package used by the planning LLM."""

    status: str
    generated_at: str
    queries: list[str]
    source_results: list[dict[str, Any]]
    skill_cards: list[dict[str, Any]]
    analysis_report: dict[str, Any]
    model_capabilities: dict[str, Any]
    viral_video_signals: list[str]
    competitor_signals: list[str]
    operation_data_signals: list[str]
    gaps: list[str]
    prompt_context: str
    boundary: str


def _clean_optional_text(value: str | None) -> str | None:
    return value.strip() if value and value.strip() else None


def _status_code_from_value_error(exc: ValueError) -> int:
    message = str(exc).lower()
    return 404 if "not found" in message else 400


def _planning_intelligence_queries(request: CommercialOperationPlanningIntelligenceRequest) -> list[str]:
    topic = request.topic.strip()
    platform = (request.platform or "短视频平台").strip()
    audience = (request.target_audience or "目标用户").strip()
    objective = (request.objective or "").strip()
    base = " ".join(piece for piece in [topic, objective] if piece).strip()[:180]
    candidates = [
        f"{platform} KTV 探店 团购 短视频 爆款 评论区",
        "site:douyin.com KTV 团购 探店 短视频",
        "site:xiaohongshu.com KTV 探店 团购 笔记",
        "KTV 本地生活 团购 到店转化 案例 数据",
        "site:oceanengine.com 本地生活 到店转化 案例",
        f"{platform} KTV 团购 到店转化 短视频 运营 案例",
        "KTV 探店 短视频 爆款 运营 打法",
        "本地生活 到店转化 短视频 运营 数据 指标",
        "数字人 短视频 本地生活 运营 案例",
        f"{platform} {audience} 团购 预约 核销 短视频 运营 数据",
        f"{base} 同题材 爆款视频 运营打法",
        "抖音生活服务 本地生活 商家 短视频 到店转化 数据 指标",
        "巨量引擎 本地生活 短视频 运营 案例 到店转化",
        "小红书 KTV 探店 团购 笔记 热门 运营",
        "本地生活商家 短视频 评论区 私信 团购 转化",
    ]
    seen: set[str] = set()
    queries: list[str] = []
    for query in candidates:
        clean_query = " ".join(query.split())[:300]
        if clean_query and clean_query not in seen:
            seen.add(clean_query)
            queries.append(clean_query)
    return queries[:8]


def _is_relevant_planning_result(item: dict[str, Any], request: CommercialOperationPlanningIntelligenceRequest) -> bool:
    text = " ".join(str(item.get(key) or "") for key in ("title", "snippet", "url")).lower()
    subject_terms = {
        "ktv",
        "karaoke",
        "抖音",
        "douyin",
        "小红书",
        "xiaohongshu",
        "生活服务",
        "本地生活",
        "本地",
        "门店",
        "商家",
        "达人",
    }
    operation_terms = {
        "短视频",
        "视频",
        "爆款",
        "到店",
        "团购",
        "核销",
        "预约",
        "探店",
        "运营",
        "转化",
        "数字人",
        "直播",
        "数据",
        "指标",
        "案例",
        "营销",
        "评论",
        "私信",
    }
    topic_terms = {
        term.lower()
        for term in re.split(r"[\s,，、|/]+", request.topic)
        if len(term.strip()) >= 2
    }
    blocked_terms = {
        "download",
        "login",
        "登录",
        "注册",
        "隐私政策",
        "用户协议",
        "app store",
        "microsoft store",
        "apps.microsoft.com",
        "vercel.app",
        "log_out",
        "buyin.jinritemai.com",
        "官方下载安装",
        "百度百科",
        "股票",
        "游戏攻略",
    }
    if any(term in text for term in blocked_terms):
        return False
    subject_hits = sum(1 for term in subject_terms if term in text)
    operation_hits = sum(1 for term in operation_terms if term in text)
    topic_hits = sum(1 for term in topic_terms if term in text)
    return (subject_hits >= 1 and operation_hits >= 1) or (operation_hits >= 2 and topic_hits >= 1)


def _extract_duckduckgo_url(raw_url: str) -> str:
    if not raw_url:
        return ""
    if raw_url.startswith("//"):
        raw_url = f"https:{raw_url}"
    parsed = urlparse(raw_url)
    if parsed.netloc.endswith("duckduckgo.com") and parsed.path.startswith("/l/"):
        target = parse_qs(parsed.query).get("uddg", [""])[0]
        return unquote(target) if target else raw_url
    return raw_url


def _extract_bing_url(raw_url: str) -> str:
    if not raw_url:
        return ""
    raw_url = html.unescape(raw_url)
    if raw_url.startswith("//"):
        raw_url = f"https:{raw_url}"
    parsed = urlparse(raw_url)
    if parsed.netloc.endswith("bing.com") and parsed.path.startswith("/ck/"):
        target = parse_qs(parsed.query).get("u", [""])[0]
        if target.startswith("a1"):
            try:
                import base64

                encoded = target[2:]
                padded = encoded + "=" * (-len(encoded) % 4)
                return base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8", errors="ignore")
            except Exception:  # noqa: BLE001 - preserve the original redirect if Bing changes the format.
                return raw_url
        return unquote(target) if target else raw_url
    if raw_url.startswith("/"):
        return f"https://www.bing.com{raw_url}"
    return raw_url


def _strip_html(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    text = html.unescape(text)
    return " ".join(text.split())


def _source_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:  # noqa: BLE001 - display helper only.
        return ""


def _source_path(url: str) -> str:
    try:
        return urlparse(url).path.rstrip("/")
    except Exception:  # noqa: BLE001 - display helper only.
        return ""


def _is_generic_platform_homepage(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except Exception:  # noqa: BLE001 - display helper only.
        return False
    domain = parsed.netloc.replace("www.", "").lower()
    path = parsed.path.rstrip("/")
    generic_domains = {
        "douyin.com",
        "eos.douyin.com",
        "oceanengine.com",
        "xiaohongshu.com",
        "kuaishou.com",
        "bilibili.com",
    }
    generic_paths = {"", "/", "/login", "/passport/login", "/download"}
    return any(domain == item or domain.endswith(f".{item}") for item in generic_domains) and path in generic_paths


def _classify_planning_source(
    item: dict[str, Any],
    request: CommercialOperationPlanningIntelligenceRequest,
) -> dict[str, Any]:
    classified = dict(item)
    url = str(classified.get("url") or "")
    title = str(classified.get("title") or "")
    snippet = str(classified.get("snippet") or "")
    query = str(classified.get("query") or "")
    source = str(classified.get("source") or "")
    domain = _source_domain(url)
    text = " ".join([title, snippet, url, query]).lower()
    classified["domain"] = domain
    classified["matched_query"] = query

    topic_terms = {term.lower() for term in re.split(r"[\s,，、|/]+", request.topic) if len(term.strip()) >= 2}
    video_terms = {"短视频", "视频", "探店", "爆款", "评论区", "douyin.com", "xiaohongshu.com", "小红书", "案例"}
    data_terms = {"数据", "指标", "转化", "核销", "团购", "预约", "点击", "互动", "复盘", "报告", "白皮书"}
    platform_terms = {"规则", "文档", "生活服务", "商家", "平台", "resource", "docs", "oceanengine"}

    topic_hits = sum(1 for term in topic_terms if term and term in text)
    video_hits = sum(1 for term in video_terms if term.lower() in text)
    data_hits = sum(1 for term in data_terms if term.lower() in text)
    platform_hits = sum(1 for term in platform_terms if term.lower() in text)
    is_homepage = _is_generic_platform_homepage(url)
    is_platform_reference = source == "platform_reference" or is_homepage
    is_case_reference = source == "case_reference"

    if is_platform_reference:
        evidence_type = "platform_reference"
        evidence_label = "平台规则/经营资料"
        source_role = "reference_only"
        reason = "这是平台公开资料或官网入口，只能用于规则、产品边界和经营流程参考，不能当作爆款或真实运营数据。"
        score = 42 if is_homepage else min(62, 44 + platform_hits * 4 + data_hits)
    elif is_case_reference:
        evidence_type = "operation_data_or_method"
        evidence_label = "案例/方法参考"
        source_role = "plan_evidence"
        reason = "这是具体案例或方法页，可用于形成打法假设，但仍不是项目后台真实数据。"
        score = min(82, 58 + topic_hits * 4 + data_hits * 3 + video_hits * 2)
    elif video_hits >= 2 and topic_hits >= 1 and not is_homepage:
        evidence_type = "same_topic_video_or_case"
        evidence_label = "同题材/案例线索"
        source_role = "plan_evidence"
        reason = "标题、摘要或链接同时命中项目题材与短视频/探店/案例词，可作为方案拆解线索。"
        score = min(95, 62 + topic_hits * 8 + video_hits * 4 + data_hits * 2)
    elif data_hits >= 2 and not is_homepage:
        evidence_type = "operation_data_or_method"
        evidence_label = "运营数据/方法"
        source_role = "plan_evidence"
        reason = "结果命中转化、团购、核销、指标或复盘口径，可用于形成运营假设。"
        score = min(88, 56 + topic_hits * 6 + data_hits * 5 + platform_hits * 2)
    elif platform_hits >= 2:
        evidence_type = "platform_reference"
        evidence_label = "平台规则/经营资料"
        source_role = "reference_only"
        reason = "这是平台公开资料或经营说明，只能作为规则和流程参考。"
        score = 42 if is_homepage else min(68, 46 + platform_hits * 4 + data_hits * 2)
    else:
        evidence_type = "weak_reference"
        evidence_label = "弱相关"
        source_role = "reference_only"
        reason = "相关性不足或缺少可验证运营信息，保留为待人工复核来源。"
        score = min(45, 20 + topic_hits * 5 + video_hits * 3 + data_hits * 3)

    if ("site:douyin.com" in query.lower() or "site:xiaohongshu.com" in query.lower()) and not is_homepage:
        reason = f"命中定向搜索词“{query[:80]}”，需要打开后人工确认具体内容页是否可用。"
        if evidence_type == "weak_reference":
            evidence_type = "same_topic_video_or_case"
            evidence_label = "同题材/案例线索"
            source_role = "plan_evidence"
            score = max(score, 58)

    classified.update({
        "evidence_type": evidence_type,
        "evidence_label": evidence_label,
        "source_role": source_role,
        "relevance_reason": reason,
        "actionability_score": score,
        "generic_homepage": is_homepage,
        "source_path": _source_path(url),
    })
    if is_homepage and not snippet:
        classified["snippet"] = "平台官网首页只作为入口参考；不计入同题材爆款、案例或运营数据证据。"
    return classified


async def _enrich_source_visuals(results: list[dict[str, Any]], *, limit: int = 8) -> list[dict[str, Any]]:
    enriched = [dict(item) for item in results]
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ),
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.6",
    }
    async def enrich_one(client: httpx.AsyncClient, item: dict[str, Any]) -> None:
        url = str(item.get("url") or "")
        item["domain"] = _source_domain(url)
        item["visual_type"] = "network_reference"
        if not url.startswith(("http://", "https://")):
            return
        try:
            response = await client.get(url, headers=headers)
            body = response.text[:300_000]
        except Exception as exc:  # noqa: BLE001 - keep source even when visual metadata fails.
            item["visual_error"] = exc.__class__.__name__
            return
        image_match = re.search(
            r'<meta[^>]+(?:property|name)=["\'](?:og:image|twitter:image)["\'][^>]+content=["\']([^"\']+)["\']',
            body,
            flags=re.IGNORECASE,
        ) or re.search(
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\'](?:og:image|twitter:image)["\']',
            body,
            flags=re.IGNORECASE,
        )
        if image_match:
            image_url = html.unescape(image_match.group(1)).strip()
            if image_url.startswith("//"):
                image_url = f"https:{image_url}"
            elif image_url.startswith("/"):
                parsed = urlparse(url)
                image_url = f"{parsed.scheme}://{parsed.netloc}{image_url}"
            item["preview_image_url"] = image_url
        favicon_match = re.search(
            r'<link[^>]+rel=["\'][^"\']*(?:icon|shortcut icon)[^"\']*["\'][^>]+href=["\']([^"\']+)["\']',
            body,
            flags=re.IGNORECASE,
        )
        if favicon_match:
            favicon_url = html.unescape(favicon_match.group(1)).strip()
            if favicon_url.startswith("//"):
                favicon_url = f"https:{favicon_url}"
            elif favicon_url.startswith("/"):
                parsed = urlparse(url)
                favicon_url = f"{parsed.scheme}://{parsed.netloc}{favicon_url}"
            item["favicon_url"] = favicon_url

    async with httpx.AsyncClient(timeout=2.5, follow_redirects=True, trust_env=False) as client:
        await asyncio.gather(*(enrich_one(client, item) for item in enriched[:limit]))
    return enriched


async def _fetch_duckduckgo_results(query: str, limit: int) -> list[dict[str, Any]]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        )
    }
    async with httpx.AsyncClient(timeout=8.0, follow_redirects=True, trust_env=False) as client:
        response = await client.get("https://duckduckgo.com/html/", params={"q": query}, headers=headers)
        response.raise_for_status()
    body = response.text
    blocks = re.findall(r'<div class="result(?: result--\w+)?">([\s\S]*?)</div>\s*</div>', body)
    results: list[dict[str, Any]] = []
    for block in blocks:
        link_match = re.search(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>([\s\S]*?)</a>', block)
        if not link_match:
            continue
        url = _extract_duckduckgo_url(html.unescape(link_match.group(1)))
        title = _strip_html(link_match.group(2))
        snippet_match = re.search(r'<a[^>]+class="result__snippet"[^>]*>([\s\S]*?)</a>', block)
        snippet = _strip_html(snippet_match.group(1)) if snippet_match else ""
        if title and url:
            results.append({
                "query": query,
                "title": title[:300],
                "url": url,
                "snippet": snippet[:500],
                "source": "duckduckgo_html",
            })
        if len(results) >= limit:
            break
    return results


async def _fetch_bing_results(query: str, limit: int) -> list[dict[str, Any]]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ),
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.6",
    }
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, trust_env=False) as client:
        response = await client.get("https://www.bing.com/search", params={"q": query}, headers=headers)
        response.raise_for_status()
    blocks = re.findall(r'<li class="b_algo"[\s\S]*?</li>', response.text)
    results: list[dict[str, Any]] = []
    for block in blocks:
        link_match = re.search(r"<h2[^>]*>\s*<a[^>]+href=\"([^\"]+)\"[^>]*>([\s\S]*?)</a>", block)
        if not link_match:
            continue
        title = _strip_html(link_match.group(2))
        url = _extract_bing_url(link_match.group(1))
        snippet_match = re.search(r'<p[^>]*class="[^"]*b_lineclamp[^"]*"[^>]*>([\s\S]*?)</p>', block)
        if not snippet_match:
            snippet_match = re.search(r"<p[^>]*>([\s\S]*?)</p>", block)
        snippet = _strip_html(snippet_match.group(1)) if snippet_match else ""
        if title and url:
            results.append({
                "query": query,
                "title": title[:300],
                "url": url,
                "snippet": snippet[:500],
                "source": "bing_search",
            })
        if len(results) >= limit:
            break
    return results


async def _fetch_bing_video_results(query: str, limit: int) -> list[dict[str, Any]]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ),
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.6",
    }
    video_query = f"{query} 视频"
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, trust_env=False) as client:
        response = await client.get("https://www.bing.com/videos/search", params={"q": video_query}, headers=headers)
        response.raise_for_status()
    body = response.text
    candidates = re.findall(r'<a[^>]+href="([^"]+)"[^>]*(?:title|aria-label)="([^"]+)"[^>]*>', body)
    results: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw_url, raw_title in candidates:
        url = _extract_bing_url(raw_url)
        title = _strip_html(raw_title)
        if not title or not url.startswith(("http://", "https://")) or url in seen:
            continue
        if any(blocked in url.lower() for blocked in ("bing.com/videos", "javascript:", "login")):
            continue
        seen.add(url)
        results.append({
            "query": video_query,
            "title": title[:300],
            "url": url,
            "snippet": "Bing 视频搜索结果；需打开后人工确认视频内容、账号和发布时间。",
            "source": "bing_video_search",
        })
        if len(results) >= limit:
            break
    return results


def _planning_intelligence_fallback(request: CommercialOperationPlanningIntelligenceRequest) -> dict[str, Any]:
    platform = request.platform or "短视频平台"
    topic = request.topic.strip()
    return {
        "viral_video_signals": [
            f"围绕“{topic}”补抓同题材高互动短视频：开场钩子、封面标题、评论区高频问题、转化 CTA。",
            f"对比 {platform} 上同类本地生活到店转化内容：实拍氛围、套餐拆解、人物口播、价格表达边界。",
            "记录爆款样本的镜头结构、时长、发布时间、评论触发点和可复用脚本模板。",
        ],
        "competitor_signals": [
            "补齐 3-5 个竞品/同类账号：栏目结构、发布频次、内容形态、团购/预约入口和互动话术。",
            "区分门店实拍、达人探店、数字人口播、活动短视频四类打法，避免只做单一形态。",
            "把竞品可借鉴点和不可复制风险分开写入方案审核材料。",
        ],
        "operation_data_signals": [
            "运营数据需要按播放、完播、互动、私信咨询、团购点击、预约/核销拆分，不能只看播放量。",
            "首轮方案应建立基线：每周内容量、发布时间、素材类型、CTA、转化口径和复盘节奏。",
            "若无公开可信数据，必须在方案中列为待回流指标，而不是编造行业均值。",
        ],
        "gaps": [
            "外部搜索源不可用或未返回足够结果时，需要人工补充爆款视频链接。",
            "缺少平台后台真实指标，需要发布后通过数据回流补齐。",
            "竞品账号、团购页和本地门店数据需要操作员确认来源合法性。",
        ],
    }


def _planning_reference_sources(request: CommercialOperationPlanningIntelligenceRequest) -> list[dict[str, Any]]:
    topic = request.topic.strip()
    platform = request.platform or "短视频平台"
    query = f"{platform} {topic} 公开经营参考"
    return [
        {
            "query": query,
            "title": "抖音生活服务｜本地直播专业版",
            "url": "https://eos.douyin.com/",
            "snippet": "抖音生活服务面向本地生活商家和达人提供直播经营方案，可作为本地到店转化、直播/短视频联动和商家经营链路的公开参考。",
            "source": "platform_reference",
        },
        {
            "query": query,
            "title": "抖音生活服务公开经营资料",
            "url": "https://eos.douyin.com/",
            "snippet": "抖音生活服务公开资料可作为本地生活商家短视频、团购、直播和到店转化经营链路参考。",
            "source": "platform_reference",
        },
        {
            "query": query,
            "title": "巨量引擎营销资源",
            "url": "https://www.oceanengine.com/resource",
            "snippet": "巨量引擎营销资源包含成功案例、营销观察和经营资料，可用于补充短视频内容种草、达人/商家经营和本地生活营销打法参考。",
            "source": "platform_reference",
        },
        {
            "query": query,
            "title": "巨量引擎共擎奖案例：本地生活与本地推经营案例",
            "url": "https://agent.oceanengine.com/mobile/awardsDetail/17176",
            "snippet": "巨量引擎案例展示本地生活经营、短视频兴趣种草、直播破圈和本地推流量配合，可用于形成竞品打法和转化链路假设。",
            "source": "case_reference",
        },
    ]


def _build_planning_intelligence_prompt_context(
    *,
    source_results: list[dict[str, Any]],
    skill_cards: list[dict[str, Any]],
    analysis_report: dict[str, Any],
    model_capabilities: dict[str, Any],
    viral_video_signals: list[str],
    competitor_signals: list[str],
    operation_data_signals: list[str],
    gaps: list[str],
) -> str:
    source_lines = [
        (
            f"- [{item.get('evidence_label') or item.get('source') or '来源'}]"
            f"[{item.get('source_role') or 'unknown'}]"
            f"[score={item.get('actionability_score', 'n/a')}] "
            f"{item.get('title')} | {item.get('url')} | "
            f"{item.get('relevance_reason') or item.get('snippet') or '无摘要'}"
        )
        for item in source_results[:10]
    ] or ["- 未抓取到可用外部结果，按缺口清单要求人工补充。"]
    skill_lines = [
        (
            f"- {item.get('title')}：状态 {item.get('status')}，证据 {item.get('evidence_count')} 条；"
            f"输出：{'；'.join(str(output) for output in item.get('outputs', [])[:3]) or '待补充'}；"
            f"缺口：{'；'.join(str(gap) for gap in item.get('gaps', [])[:2]) or '无'}"
        )
        for item in skill_cards
    ] or ["- 暂无结构化情报 skill 输出。"]
    return "\n".join([
        "全网运营情报（用于方案生成，不等同于人工审批）：",
        "模型分工与接入能力：",
        f"- Codex 全局控制器：{model_capabilities.get('codex_global_controller', {})}",
        f"- 主方案 LLM：{model_capabilities.get('primary_llm', {})}",
        f"- 视频分析模型：{model_capabilities.get('video_analysis_model', {})}",
        f"- 图片生成模型：{model_capabilities.get('image_generation_model', {})}",
        f"- 数据分析模型：{model_capabilities.get('data_analysis_model', {})}",
        "高价值运营分析报告：",
        f"- 证据质量：{analysis_report.get('evidence_quality_gate', {})}",
        f"- 视频分析：{analysis_report.get('video_analysis', [])}",
        f"- 竞品打法：{analysis_report.get('competitor_playbook', [])}",
        f"- 运营能力诊断：{analysis_report.get('operation_capability_diagnosis', [])}",
        f"- 数据验证计划：{analysis_report.get('data_validation_plan', [])}",
        "后台情报能力运行摘要（不需要展示给操作员）：",
        *skill_lines,
        "同题材爆款/视频线索：",
        *[f"- {item}" for item in viral_video_signals],
        "竞品/同类产品运营线索：",
        *[f"- {item}" for item in competitor_signals],
        "运营数据与指标口径：",
        *[f"- {item}" for item in operation_data_signals],
        "来源结果：",
        *source_lines,
        "情报缺口：",
        *[f"- {item}" for item in gaps],
    ])


def _build_planning_analysis_report(
    *,
    request: CommercialOperationPlanningIntelligenceRequest,
    source_results: list[dict[str, Any]],
    skill_cards: list[dict[str, Any]],
    viral_video_signals: list[str],
    competitor_signals: list[str],
    operation_data_signals: list[str],
    gaps: list[str],
) -> dict[str, Any]:
    topic = request.topic.strip()
    platform = request.platform or "短视频平台"
    plan_evidence = [item for item in source_results if str(item.get("source_role") or "") == "plan_evidence"]
    reference_only = [item for item in source_results if str(item.get("source_role") or "") == "reference_only"]
    video_sources = [
        item for item in plan_evidence
        if str(item.get("evidence_type") or "") == "same_topic_video_or_case"
        or str(item.get("source") or "") == "bing_video_search"
    ]
    case_sources = [
        item for item in plan_evidence
        if str(item.get("evidence_type") or "") == "operation_data_or_method"
        or re.search(r"案例|打法|本地生活|团购|到店|转化", " ".join(str(item.get(key) or "") for key in ("title", "snippet", "relevance_reason")))
    ]
    quality_status = "usable" if len(plan_evidence) >= 3 and len(video_sources) >= 1 else "weak"
    quality_note = (
        "已有可用于形成方案假设的公开证据，但仍需人工打开来源复核。"
        if quality_status == "usable"
        else "公开搜索结果不足以支撑强结论，方案必须以运营框架、待验证指标和人工补充素材为主。"
    )
    return {
        "evidence_quality_gate": {
            "status": quality_status,
            "plan_evidence_count": len(plan_evidence),
            "video_evidence_count": len(video_sources),
            "reference_only_count": len(reference_only),
            "decision": quality_note,
            "must_not_claim": "不得把平台官网、搜索摘要或未打开视频写成已验证爆款数据；不得虚构播放量、转化率或竞品后台指标。",
        },
        "video_analysis": [
            {
                "pattern": "本地到店强钩子短视频",
                "why_it_works": "先解决用户去哪玩、多少钱、适合几个人的问题，再给预约或团购动作，适合 KTV/本地生活转化场景。",
                "shot_structure": ["0-3 秒：预算/场景冲突钩子", "4-12 秒：包厢、音响、套餐和人群场景实拍", "13-25 秒：到店路线、套餐边界、预约方式", "结尾：评论关键词或私信 CTA"],
                "operator_action": "要求文案与影音任务至少产出 3 条脚本，每条都绑定封面文案、镜头清单、CTA 和风险提示。",
                "validation": "发布后在数据回流板块验证播放、互动、私信/团购点击、预约和核销。",
            },
            {
                "pattern": "朋友局/生日局场景化内容",
                "why_it_works": "把抽象 KTV 服务变成具体使用场景，降低用户决策成本，便于评论区询问人数、价格和时段。",
                "shot_structure": ["门店外观或商圈入口", "包厢氛围与设备", "套餐内容与人数适配", "预约/团购规则提示"],
                "operator_action": "素材上传阶段必须补齐门店实拍、包厢图、套餐说明和授权证明。",
                "validation": "比较朋友局、生日局、下班局三个栏目在互动率和咨询量上的差异。",
            },
            {
                "pattern": "数字人口播 + 实拍素材混剪",
                "why_it_works": "数字人负责清楚说明套餐和风险边界，实拍素材负责建立真实感，适合持续批量生产。",
                "shot_structure": ["数字人开场讲利益点", "门店/包厢素材切入", "套餐和规则字幕卡", "评论问题引导"],
                "operator_action": "影音生产只在素材授权和工作流选择通过后启动，不能在方案阶段直接生成最终作品。",
                "validation": "用首轮数据比较数字人口播与纯实拍内容的停留、互动和咨询差异。",
            },
        ],
        "competitor_playbook": [
            {
                "playbook": "栏目拆分打法",
                "content": "把内容拆成门店体验、套餐预算、本地热点/节日活动三条栏目，避免每条都像泛泛宣传。",
                "reuse_boundary": "可复用栏目结构和提问方式，不复用竞品素材、价格承诺和未授权人物画面。",
                "approval_focus": "审核每条内容是否有明确客群、场景、CTA 和可回流指标。",
            },
            {
                "playbook": "评论区问题驱动",
                "content": "围绕人数、价格、时段、是否适合生日/朋友聚会设置评论引导，把评论转成私信或团购咨询。",
                "reuse_boundary": "不得承诺固定最低价或固定房态；价格和时段以门店确认为准。",
                "approval_focus": "发布文案需保留价格边界、预约边界和人工确认入口。",
            },
            {
                "playbook": "短视频到发布包闭环",
                "content": "每条内容从脚本、封面、字幕、CTA 到发布正文和回流指标打包审核，减少生产和发布割裂。",
                "reuse_boundary": "公开资料只能指导流程，不代表已有项目表现。",
                "approval_focus": "方案批准后先生成文案任务，再进入影音任务和预览审批。",
            },
        ],
        "operation_capability_diagnosis": [
            {
                "capability": "素材能力",
                "current_gap": "若没有门店实拍、套餐说明、授权素材和参考视频，方案只能停留在方向层。",
                "required_action": "创建项目后先在知识库/素材上传导入门店图、包厢图、套餐表、授权证明和 3-5 个参考视频链接。",
            },
            {
                "capability": "内容生产能力",
                "current_gap": "方案必须能拆成文案、影音、封面/海报、发布包，不应只给一段口头建议。",
                "required_action": "每个栏目都要输出脚本要求、镜头要求、封面要求、发布时间和审批口径。",
            },
            {
                "capability": "运营复盘能力",
                "current_gap": "方案阶段没有真实回流数据，不能画假图表或写确定性数据结论。",
                "required_action": "只定义待验证指标；真实数据进入数据回流板块后再生成复盘和下一轮优化。",
            },
        ],
        "data_validation_plan": [
            {"metric": "播放量", "purpose": "判断选题和开场钩子吸引力", "source": "发布后平台回流", "stage": "数据回流板块"},
            {"metric": "互动率", "purpose": "判断评论引导、场景共鸣和封面标题效果", "source": "发布后平台回流", "stage": "数据回流板块"},
            {"metric": "私信/团购点击", "purpose": "判断 CTA 与套餐表达是否带来转化意向", "source": "发布后平台回流或人工记录", "stage": "数据回流板块"},
            {"metric": "预约/核销", "purpose": "判断内容是否真正带来到店结果", "source": "门店或平台后台回填", "stage": "数据回流板块"},
        ],
        "source_quality_summary": [
            {
                "title": str(item.get("title") or "公开来源"),
                "role": str(item.get("source_role") or "reference_only"),
                "use": str(item.get("relevance_reason") or item.get("snippet") or "需要人工复核"),
                "url": str(item.get("url") or ""),
            }
            for item in source_results[:6]
        ],
        "backend_capabilities_used": [str(item.get("skill_key") or item.get("title") or "") for item in skill_cards],
        "gaps": gaps,
        "plan_generation_requirement": (
            "LLM 必须把以上分析转成完整方案：目标拆解、栏目策略、视频结构、竞品打法、素材清单、生产任务、审批口径、"
            "发布节奏和数据验证计划；不要输出泛泛建议，不要把待回流指标写成已发生数据。"
        ),
    }


def _build_planning_model_capabilities() -> dict[str, Any]:
    settings = get_settings()
    llm_provider = settings.llm_provider.strip().lower()
    primary_llm_model = (
        settings.operation_planning_llm_model.strip()
        or (settings.local_llm_model if llm_provider == "local" else settings.server_llm_model)
    )
    data_model = settings.operation_planning_data_analysis_model.strip() or primary_llm_model
    video_agent = CommercialVideoAgent()
    documents = video_agent.workflow_knowledge.load_documents()
    capability_counts = video_agent.workflow_knowledge.capability_counts(documents)
    runtime_evidence = video_agent._runtime_evidence(documents=documents, capability_counts=capability_counts)
    minimum = runtime_evidence.get("video_minimum_capabilities_present")
    minimum_caps = minimum if isinstance(minimum, dict) else {}
    video_analysis_ready = bool(
        settings.operation_planning_multimodal_enabled
        and settings.operation_planning_video_analysis_enabled
        and settings.comfyui_runtime_enabled
        and minimum_caps.get("video_analysis")
        and (minimum_caps.get("vlm_prompting") or capability_counts.get("vlm_prompting", 0) > 0)
    )
    image_generation_ready = bool(
        settings.operation_planning_multimodal_enabled
        and settings.comfyui_runtime_enabled
        and minimum_caps.get("image_generation")
    )
    return {
        "enabled": settings.operation_planning_multimodal_enabled,
        "codex_global_controller": {
            "enabled": settings.codex_global_controller_enabled,
            "provider": settings.codex_global_controller_provider,
            "model": settings.codex_global_controller_model,
            "mode": settings.codex_global_controller_mode,
            "scope": [
                item.strip()
                for item in settings.codex_global_controller_scope.split(",")
                if item.strip()
            ],
            "role": (
                "全局把控运营闭环：拆解阶段、选择模型/Agent、检查证据质量、保持数据回流边界、"
                "监督审批闸门，并把方案、生产、发布和复盘串成同一项目状态机。"
            ),
            "human_approval_required": settings.codex_global_controller_requires_human_approval,
            "forbidden_actions": [
                "不直接绕过人工审批",
                "不把方案阶段的待验证指标写成真实回流数据",
                "不直接提交 ComfyUI 队列",
                "不控制真实平台账号或发布",
                "不替代视频分析、图片生成和数据分析专用模型",
            ],
        },
        "primary_llm": {
            "provider": llm_provider,
            "model": primary_llm_model,
            "role": "负责整合项目目标、公开情报、知识库和各分析模型输出，生成可审批运营方案。",
            "limitation": "如果只依赖文本模型，不能完成真实视频理解、画面质量判断或图片生成。",
        },
        "video_analysis_model": {
            "provider": settings.operation_planning_vlm_provider,
            "model": settings.operation_planning_vlm_model,
            "ready": video_analysis_ready,
            "role": "分析参考视频、关键帧、口播/字幕、镜头节奏、场景元素和可复用边界。",
            "required_capabilities": ["video_analysis", "vlm_prompting", "asr"],
            "available_capabilities": {
                "video_analysis": bool(minimum_caps.get("video_analysis")),
                "vlm_prompting": bool(minimum_caps.get("vlm_prompting")),
                "asr": bool(minimum_caps.get("asr")),
            },
        },
        "image_generation_model": {
            "provider": settings.operation_planning_image_generation_provider,
            "model": settings.operation_planning_image_generation_model,
            "ready": image_generation_ready,
            "role": "生成或编辑封面、首帧、海报、素材卡和审核预览图；方案阶段只生成需求和工作流选择，不直接绕过审批产出最终作品。",
            "required_capabilities": ["image_generation", "segmentation"],
            "available_capabilities": {
                "image_generation": bool(minimum_caps.get("image_generation")),
                "segmentation": capability_counts.get("segmentation", 0) > 0,
            },
        },
        "data_analysis_model": {
            "provider": llm_provider,
            "model": data_model,
            "ready": True,
            "role": "方案阶段负责指标口径、实验设计、数据验证计划；真实数据只在数据回流板块进入。",
            "boundary": "不得在方案阶段生成假回流图表或伪造平台指标。",
        },
        "workflow_runtime": {
            "provider": "comfyui_cu130",
            "enabled": settings.comfyui_runtime_enabled,
            "base_url": settings.comfyui_runtime_base_url,
            "workflow_knowledge_path": str(video_agent.workflow_knowledge.knowledge_path),
            "workflow_candidate_count": len(documents),
            "capability_counts": capability_counts,
            "runtime_evidence": runtime_evidence,
            "use_video_agent_workflows": settings.operation_planning_use_video_agent_workflows,
        },
        "routing_policy": [
            "Codex 全局控制器负责阶段路由、模型分工、证据质量和审批边界。",
            "运营方案文本与决策结构交给 primary_llm。",
            "参考视频、关键帧、口播和画面结构交给 video_analysis_model。",
            "封面、首帧、海报和素材卡交给 image_generation_model 或 ComfyUI 工作流候选。",
            "播放、互动、咨询、团购、预约和核销只在数据回流板块进入 data_analysis_model。",
            "任何 ComfyUI 队列提交、真实发布和账号操作都必须等待人工审批和运行闸门。",
        ],
    }


def _build_planning_research_skill_cards(
    *,
    queries: list[str],
    source_results: list[dict[str, Any]],
    viral_video_signals: list[str],
    competitor_signals: list[str],
    operation_data_signals: list[str],
    gaps: list[str],
) -> list[dict[str, Any]]:
    def indexes_for(predicate: Any) -> list[int]:
        return [index + 1 for index, item in enumerate(source_results) if predicate(item)]

    def source_titles(indexes: list[int], fallback: list[str]) -> list[str]:
        outputs = [
            str(source_results[index - 1].get("title") or source_results[index - 1].get("domain") or "外部来源")
            for index in indexes[:3]
            if 0 <= index - 1 < len(source_results)
        ]
        return outputs or fallback[:3]

    plan_evidence_indexes = indexes_for(lambda item: str(item.get("source_role") or "") == "plan_evidence")
    reference_indexes = indexes_for(lambda item: str(item.get("source_role") or "") == "reference_only")
    video_indexes = indexes_for(
        lambda item: str(item.get("evidence_type") or "") == "same_topic_video_or_case"
        or str(item.get("source") or "") == "bing_video_search"
    )
    competitor_indexes = indexes_for(
        lambda item: str(item.get("evidence_type") or "") in {"operation_data_or_method", "same_topic_video_or_case"}
        and re.search(r"竞品|案例|打法|探店|团购|到店|转化", " ".join(str(item.get(key) or "") for key in ("title", "snippet", "relevance_reason")))
    )
    metric_indexes = indexes_for(
        lambda item: re.search(r"数据|指标|转化|核销|团购|预约|点击|互动|复盘", " ".join(str(item.get(key) or "") for key in ("title", "snippet", "relevance_reason")))
    )

    return [
        {
            "skill_key": "public_search_skill",
            "title": "全网搜索技能",
            "purpose": "按项目主题、平台和到店转化目标生成多组搜索词，抓取公开网页、视频搜索和平台经营资料。",
            "status": "ready" if source_results else "gap",
            "evidence_count": len(source_results),
            "source_indexes": list(range(1, len(source_results) + 1))[:8],
            "outputs": [f"已执行 {len(queries)} 组搜索词", f"筛出 {len(plan_evidence_indexes)} 条方案依据", f"标记 {len(reference_indexes)} 条平台参考"],
            "gaps": gaps[:2] if len(plan_evidence_indexes) < 2 else [],
            "boundary": "只使用公开搜索结果；不会伪装成平台后台或账号真实数据。",
        },
        {
            "skill_key": "hot_video_signal_skill",
            "title": "热门视频线索技能",
            "purpose": "从视频搜索、同题材案例和短视频关键词中提取爆款结构、封面标题、评论触发点和可复用边界。",
            "status": "ready" if video_indexes else "needs_review",
            "evidence_count": len(video_indexes),
            "source_indexes": video_indexes[:6],
            "outputs": source_titles(video_indexes, viral_video_signals),
            "gaps": [] if video_indexes else ["未拿到可直接审核的视频内容页，需要操作员补充具体爆款视频链接或打开来源复核。"],
            "boundary": "只能拆解公开表达结构，不能照搬素材、脚本或未授权画面。",
        },
        {
            "skill_key": "competitor_playbook_skill",
            "title": "竞品打法技能",
            "purpose": "整理同类门店、团购、探店、达人/数字人口播和活动短视频的栏目结构与转化动作。",
            "status": "ready" if competitor_indexes else "needs_review",
            "evidence_count": len(competitor_indexes),
            "source_indexes": competitor_indexes[:6],
            "outputs": source_titles(competitor_indexes, competitor_signals),
            "gaps": [] if competitor_indexes else ["缺少明确竞品账号、团购页和本地门店样本，需要人工确认 3-5 个可复核对象。"],
            "boundary": "竞品打法只能用于形成假设；不可复制价格承诺、素材和账号私域数据。",
        },
        {
            "skill_key": "platform_reference_skill",
            "title": "平台公开资料技能",
            "purpose": "抽取平台经营说明、公开案例、规则边界和本地生活链路，用于方案合规与流程设计。",
            "status": "ready" if reference_indexes else "gap",
            "evidence_count": len(reference_indexes),
            "source_indexes": reference_indexes[:6],
            "outputs": source_titles(reference_indexes, ["平台公开资料不足，需要补充平台规则、商家经营说明和案例页。"]),
            "gaps": [] if reference_indexes else ["未获得足够平台公开资料。"],
            "boundary": "平台官网和经营资料不等于爆款证据，也不等于项目后台数据。",
        },
        {
            "skill_key": "metric_modeling_skill",
            "title": "指标建模技能",
            "purpose": "把公开线索转成可审核 KPI、发布后回流口径和再次分析字段。",
            "status": "ready" if operation_data_signals or metric_indexes else "needs_review",
            "evidence_count": len(metric_indexes),
            "source_indexes": metric_indexes[:6],
            "outputs": source_titles(metric_indexes, operation_data_signals),
            "gaps": ["没有项目真实回流指标前，只能生成基线与验证计划，不能写成已验证结论。"],
            "boundary": "真实播放、互动、咨询、团购和核销必须由发布后数据回流补齐。",
        },
    ]


def _rag_generation_query(
    *,
    operation_title: str,
    operation_objective: str,
    deliverable_title: str,
    deliverable_summary: str | None,
    requested_query: str | None,
) -> str:
    clean_query = _clean_optional_text(requested_query)
    if clean_query:
        return clean_query
    pieces = [
        operation_title,
        operation_objective,
        deliverable_title,
        deliverable_summary or "",
    ]
    return " ".join(piece.strip() for piece in pieces if piece and piece.strip())[:1000]


def _rag_operation_query(
    *,
    operation_title: str,
    operation_objective: str,
    target_audience: str | None,
    channels: list[str] | None,
    success_metrics: list[str] | None,
    requested_query: str | None,
) -> str:
    clean_query = _clean_optional_text(requested_query)
    if clean_query:
        return clean_query
    pieces = [
        operation_title,
        operation_objective,
        target_audience or "",
        " ".join(channels or []),
        " ".join(success_metrics or []),
    ]
    return " ".join(piece.strip() for piece in pieces if piece and piece.strip())[:1000]


def _rag_evidence_item(chunk: Any) -> dict[str, Any]:
    metadata = dict(getattr(chunk, "metadata", {}) or {})
    score = (
        getattr(chunk, "rerank_score", None)
        or getattr(chunk, "hybrid_score", None)
        or getattr(chunk, "keyword_score", None)
        or getattr(chunk, "dense_score", None)
        or getattr(chunk, "similarity_score", None)
    )
    text = getattr(chunk, "text", "") or ""
    return {
        "chunk_id": getattr(chunk, "id", None),
        "document_id": metadata.get("document_id"),
        "source_id": metadata.get("source_id"),
        "chunk_index": getattr(chunk, "chunk_index", None),
        "score": score,
        "text_excerpt": text[:800],
        "metadata": metadata,
        "evidence_boundary": "retrieved from existing RAG index; not auto-approved or externally executed",
    }


def _rag_source_materials(*, collection_name: str, evidence_items: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    materials: list[str] = []
    candidates: list[str] = [f"rag:{collection_name}"]
    for item in evidence_items:
        document_id = item.get("document_id")
        source_id = item.get("source_id")
        if isinstance(document_id, str) and document_id:
            candidates.append(f"document:{document_id}")
        if isinstance(source_id, str) and source_id:
            candidates.append(f"source:{source_id}")
    for candidate in candidates:
        if candidate not in seen:
            seen.add(candidate)
            materials.append(candidate)
    return materials


def _rag_content_draft_body(
    *,
    operation_title: str,
    operation_objective: str,
    target_audience: str | None,
    channel: str,
    content_format: str,
    query: str,
    evidence_items: list[dict[str, Any]],
    call_to_action: str | None,
) -> str:
    audience = target_audience or "target audience"
    evidence_lines = [
        (
            f"- {str(item.get('text_excerpt') or '').strip()[:240]} "
            f"(document: {item.get('document_id') or 'unknown'}, source: {item.get('source_id') or 'unknown'})"
        )
        for item in evidence_items
        if str(item.get("text_excerpt") or "").strip()
    ]
    if not evidence_lines:
        evidence_lines = [
            "- No retrieved RAG chunks; revise the query or attach source material before review."
        ]
    proof_points = [
        str(item.get("text_excerpt") or "").strip()[:160]
        for item in evidence_items[:3]
        if str(item.get("text_excerpt") or "").strip()
    ]
    proof_sentence = " ".join(proof_points) if proof_points else "Evidence still needs operator review before use."
    return "\n".join(
        [
            f"Channel: {channel}",
            f"Format: {content_format}",
            f"Operation: {operation_title}",
            f"Audience: {audience}",
            f"Objective: {operation_objective}",
            f"RAG query: {query}",
            "",
            "RAG evidence used:",
            *evidence_lines,
            "",
            "Draft:",
            f"Opening: Address {audience} with the operation goal: {operation_objective}",
            f"Proof points: {proof_sentence}",
            f"Call to action: {call_to_action or 'Confirm the next step with the operator.'}",
            "",
            (
                "Review boundary: draft only; no publishing, account control, ComfyUI, OpenClaw, "
                "or browser worker action was executed."
            ),
        ]
    )


def _rag_asset_brief_query(
    *,
    operation_title: str,
    operation_objective: str,
    target_audience: str | None,
    success_metrics: list[str] | None,
    channel: str,
    asset_type: str,
    content_draft: Any | None,
    requested_query: str | None,
) -> str:
    clean_query = _clean_optional_text(requested_query)
    if clean_query:
        return clean_query
    draft_body = getattr(content_draft, "content_body", "") if content_draft else ""
    pieces = [
        operation_title,
        operation_objective,
        target_audience or "",
        " ".join(success_metrics or []),
        channel,
        asset_type,
        getattr(content_draft, "title", "") if content_draft else "",
        getattr(content_draft, "summary", "") if content_draft else "",
        str(draft_body or "")[:500],
    ]
    return " ".join(piece.strip() for piece in pieces if piece and piece.strip())[:1000]


def _rag_asset_generation_prompt(
    *,
    operation_title: str,
    operation_objective: str,
    target_audience: str | None,
    channel: str,
    asset_type: str,
    purpose: str,
    style_constraints: str,
    dimensions: str | None,
    query: str,
    evidence_items: list[dict[str, Any]],
    content_draft: Any | None,
) -> str:
    audience = target_audience or "target audience"
    evidence_lines = [
        (
            f"- {str(item.get('text_excerpt') or '').strip()[:240]} "
            f"(document: {item.get('document_id') or 'unknown'}, source: {item.get('source_id') or 'unknown'})"
        )
        for item in evidence_items
        if str(item.get("text_excerpt") or "").strip()
    ]
    if not evidence_lines:
        evidence_lines = ["- No retrieved RAG chunks; revise the query or attach source material before review."]
    draft_context = ""
    if content_draft is not None:
        draft_context = " ".join(
            piece.strip()
            for piece in [
                getattr(content_draft, "title", "") or "",
                getattr(content_draft, "summary", "") or "",
                getattr(content_draft, "call_to_action", "") or "",
            ]
            if piece and piece.strip()
        )
    return "\n".join(
        [
            f"Asset type: {asset_type}",
            f"Channel: {channel}",
            f"Operation: {operation_title}",
            f"Audience: {audience}",
            f"Objective: {operation_objective}",
            f"Purpose: {purpose}",
            f"Dimensions: {dimensions or 'operator-selected dimensions'}",
            f"Style constraints: {style_constraints}",
            f"RAG query: {query}",
            "",
            "Source evidence:",
            *evidence_lines,
            "",
            "Visual brief:",
            f"Create a reviewable {asset_type} asset brief for {channel} that supports: {operation_objective}",
            "Use the reviewed knowledge points as conceptual guidance only.",
            f"Draft context: {draft_context or 'no linked content draft'}",
            "",
            (
                "Execution boundary: brief only; no ComfyUI job, OpenClaw action, browser worker action, "
                "publishing, account control, or approval bypass was executed."
            ),
        ]
    )


def _rag_asset_readiness_checks(
    *,
    requested_checks: list[str],
    evidence_items: list[dict[str, Any]],
) -> list[str]:
    seen: set[str] = set()
    checks: list[str] = []
    candidates = [
        *requested_checks,
        "RAG search completed against existing knowledge index",
        "operator must review source materials before approval",
        "no ComfyUI job was created",
        "no publishing or account action was executed",
    ]
    if not evidence_items:
        candidates.append("no retrieved chunks; revise query or attach source material before approval")
    for candidate in candidates:
        clean_candidate = candidate.strip() if candidate else ""
        if clean_candidate and clean_candidate not in seen:
            seen.add(clean_candidate)
            checks.append(clean_candidate)
    return checks


def _unique_document_ids(evidence_items: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    document_ids: list[str] = []
    for item in evidence_items:
        document_id = item.get("document_id")
        if isinstance(document_id, str) and document_id and document_id not in seen:
            seen.add(document_id)
            document_ids.append(document_id)
    return document_ids


async def _video_agent_rag_context(
    *,
    operation: Any,
    request: CommercialOperationVideoAgentOrchestrationRequest,
    session: AsyncSession,
    workspace_id: str,
) -> dict[str, Any]:
    settings = get_settings()
    search_mode = request.search_mode or settings.default_search_mode
    if search_mode not in {"dense", "keyword", "hybrid"}:
        raise ValueError("search_mode must be dense, keyword, or hybrid")
    dense_top_k = request.dense_top_k or settings.dense_top_k
    keyword_top_k = request.keyword_top_k or settings.keyword_top_k
    final_top_k = request.final_top_k or settings.final_top_k
    query = _rag_operation_query(
        operation_title=operation.title,
        operation_objective=request.objective or operation.objective,
        target_audience=operation.target_audience,
        channels=[*(operation.channels or []), request.channel, *request.target_channels],
        success_metrics=operation.success_metrics,
        requested_query=request.query,
    )
    try:
        pipeline = create_hybrid_search_pipeline(
            settings=settings,
            session=session,
            collection_name=_clean_optional_text(request.knowledge_collection) or operation.knowledge_collection,
        )
        bundle = await pipeline.search(
            query=query,
            search_mode=search_mode,  # type: ignore[arg-type]
            dense_top_k=dense_top_k,
            keyword_top_k=keyword_top_k,
            source_id=_clean_optional_text(request.source_id),
            workspace_id=workspace_id,
        )
        reranked = await RerankerClient(settings=settings).rerank(
            query=query,
            chunks=bundle.merged_results,
            top_n=final_top_k,
        )
        retrieved_chunks = [build_retrieved_chunk_from_reranked(result) for result in reranked]
        evidence_items = [_rag_evidence_item(chunk) for chunk in retrieved_chunks]
        collection_name = pipeline.vector_store.collection_name
        return {
            "status": "complete" if evidence_items else "empty",
            "used_retrieval": bool(evidence_items),
            "query": query,
            "collection_name": collection_name,
            "source_id": _clean_optional_text(request.source_id),
            "search_mode": search_mode,
            "dense_top_k": dense_top_k,
            "keyword_top_k": keyword_top_k,
            "final_top_k": final_top_k,
            "rag_result_count": len(evidence_items),
            "dense_candidate_count": len(bundle.dense_results),
            "keyword_candidate_count": len(bundle.keyword_results),
            "merged_candidate_count": len(bundle.merged_results),
            "evidence_items": evidence_items,
            "source_materials": _rag_source_materials(collection_name=collection_name, evidence_items=evidence_items),
            "document_ids": _unique_document_ids(evidence_items),
            "boundary": "RAG evidence is used as planning context only; it is not an approval or publishing signal.",
        }
    except Exception as exc:
        logger.warning(
            "Commercial video agent RAG context fallback activated",
            extra={"operation_id": str(operation.id), "workspace_id": workspace_id, "error": str(exc)},
        )
        return {
            "status": "fallback",
            "used_retrieval": False,
            "query": query,
            "collection_name": _clean_optional_text(request.knowledge_collection) or operation.knowledge_collection,
            "source_id": _clean_optional_text(request.source_id),
            "search_mode": search_mode,
            "dense_top_k": dense_top_k,
            "keyword_top_k": keyword_top_k,
            "final_top_k": final_top_k,
            "rag_result_count": 0,
            "evidence_items": [],
            "source_materials": [],
            "document_ids": [],
            "error": str(exc),
            "boundary": "RAG lookup failed or was unavailable; operator must review the video plan with extra care.",
        }


@router.post("", response_model=CommercialOperationResponse, status_code=201)
async def create_commercial_operation(
    request: CommercialOperationCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationResponse:
    """Create a commercial operation project from a business objective."""

    try:
        operation = await CommercialOperationService(session).create_operation(
            workspace_id=context.workspace_id,
            user_id=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationResponse.from_model(operation)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Commercial operation create API failed")
        raise AppError("Commercial operation create failed", status_code=500) from exc


@router.get("", response_model=CommercialOperationListResponse)
async def list_commercial_operations(
    status: str | None = Query(default=None, description="draft / planning / ready / active / paused / completed / archived"),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationListResponse:
    """List commercial operations in the current workspace."""

    try:
        service = CommercialOperationService(session)
        operations = await service.list_operations(
            workspace_id=context.workspace_id,
            status=status,
            limit=limit,
        )
        return CommercialOperationListResponse(
            items=[
                CommercialOperationResponse.from_model(
                    operation,
                    production_closed_loop_action_audit_summary=service.production_closed_loop_action_audit_summary_for_operation(
                        operation
                    ),
                )
                for operation in operations
            ]
        )
    except Exception as exc:
        logger.exception("Commercial operation list API failed")
        raise AppError("Commercial operation list failed", status_code=500) from exc


@router.post("/planning-intelligence", response_model=CommercialOperationPlanningIntelligenceResponse)
async def collect_commercial_operation_planning_intelligence(
    request: CommercialOperationPlanningIntelligenceRequest,
) -> CommercialOperationPlanningIntelligenceResponse:
    """Collect external planning intelligence before generating an operation plan."""

    queries = _planning_intelligence_queries(request)
    source_results: list[dict[str, Any]] = []
    errors: list[str] = []
    per_query_limit = max(4, min(6, (request.max_results + max(1, min(len(queries), 8)) - 1) // max(1, min(len(queries), 8))))

    async def run_fetch(fetcher: Any, query: str) -> list[dict[str, Any]]:
        try:
            return await fetcher(query, per_query_limit)
        except Exception as exc:  # noqa: BLE001 - returned as auditable gap, not fatal.
            errors.append(f"{fetcher.__name__} {query}: {exc}")
            return []

    fetched_batches = await asyncio.gather(
        *(
            run_fetch(fetcher, query)
            for query in queries
            for fetcher in (_fetch_duckduckgo_results, _fetch_bing_results, _fetch_bing_video_results)
        )
    )
    for batch in fetched_batches:
        source_results.extend(batch)

    deduped_results: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    for item in source_results:
        url = str(item.get("url") or "")
        title = str(item.get("title") or "")
        key = url or title
        if key and key not in seen_urls and _is_relevant_planning_result(item, request):
            seen_urls.add(key)
            classified = _classify_planning_source(item, request)
            if classified.get("source_role") == "plan_evidence" or len(deduped_results) < max(4, request.max_results // 2):
                deduped_results.append(classified)
        if len(deduped_results) >= request.max_results:
            break
    deduped_results.sort(
        key=lambda item: (
            0 if str(item.get("source_role") or "") == "plan_evidence" else 1,
            -int(item.get("actionability_score") or 0),
        )
    )

    fallback = _planning_intelligence_fallback(request)
    if len(deduped_results) < min(4, request.max_results):
        for item in _planning_reference_sources(request):
            url = str(item.get("url") or "")
            title = str(item.get("title") or "")
            key = url or title
            if key and key not in seen_urls:
                seen_urls.add(key)
                deduped_results.append(_classify_planning_source(item, request))
            if len(deduped_results) >= request.max_results:
                break
    deduped_results.sort(
        key=lambda item: (
            0 if str(item.get("source_role") or "") == "plan_evidence" else 1,
            -int(item.get("actionability_score") or 0),
        )
    )
    plan_evidence_count = sum(1 for item in deduped_results if str(item.get("source_role") or "") == "plan_evidence")
    reference_only_count = sum(1 for item in deduped_results if str(item.get("source_role") or "") == "reference_only")
    status = "complete" if plan_evidence_count >= 2 else "reference_backfill"
    gaps = [*fallback["gaps"]]
    if errors:
        gaps.append(f"外部搜索部分失败：{'；'.join(errors)[:600]}")
    if deduped_results:
        gaps = [
            "需要操作员审核外部链接是否与项目场景匹配。",
            "公开视频和行业文章只能作为参考，不能替代平台后台真实数据。",
            "发布后必须通过数据回流验证方案假设。",
        ]
        if plan_evidence_count < 2:
            gaps.insert(0, "实时搜索未返回足够可用的同题材/数据证据；平台官网、规则页和经营资料已降级为仅参考，需要人工补充可验证的爆款视频、竞品账号或平台后台数据。")
        if reference_only_count:
            gaps.append(f"已将 {reference_only_count} 条官网、文档或平台资料标记为仅参考，不计入爆款或真实运营数据证据。")
    deduped_results = await _enrich_source_visuals(deduped_results, limit=min(request.max_results, 8))
    skill_cards = _build_planning_research_skill_cards(
        queries=queries,
        source_results=deduped_results,
        viral_video_signals=fallback["viral_video_signals"],
        competitor_signals=fallback["competitor_signals"],
        operation_data_signals=fallback["operation_data_signals"],
        gaps=gaps,
    )
    model_capabilities = _build_planning_model_capabilities()
    analysis_report = _build_planning_analysis_report(
        request=request,
        source_results=deduped_results,
        skill_cards=skill_cards,
        viral_video_signals=fallback["viral_video_signals"],
        competitor_signals=fallback["competitor_signals"],
        operation_data_signals=fallback["operation_data_signals"],
        gaps=gaps,
    )
    prompt_context = _build_planning_intelligence_prompt_context(
        source_results=deduped_results,
        skill_cards=skill_cards,
        analysis_report=analysis_report,
        model_capabilities=model_capabilities,
        viral_video_signals=fallback["viral_video_signals"],
        competitor_signals=fallback["competitor_signals"],
        operation_data_signals=fallback["operation_data_signals"],
        gaps=gaps,
    )
    return CommercialOperationPlanningIntelligenceResponse(
        status=status,
        generated_at=datetime.now(timezone.utc).isoformat(),
        queries=queries,
        source_results=deduped_results,
        skill_cards=skill_cards,
        analysis_report=analysis_report,
        model_capabilities=model_capabilities,
        viral_video_signals=fallback["viral_video_signals"],
        competitor_signals=fallback["competitor_signals"],
        operation_data_signals=fallback["operation_data_signals"],
        gaps=gaps,
        prompt_context=prompt_context,
        boundary=(
            "External intelligence is search evidence for planning only; operator must review sources and "
            "no publishing, account control, metric scraping, or approval bypass was executed."
        ),
    )


@router.get("/metric-analysis-dispatch", response_model=CommercialOperationMetricAnalysisDispatchQueueResponse)
async def get_commercial_operation_metric_analysis_dispatch_queue(
    platform: str | None = Query(default=None, description="Optional platform filter, for example douyin"),
    force: bool = Query(default=False, description="Force due-state preparation without changing project schedules"),
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMetricAnalysisDispatchQueueResponse:
    """Read the workspace-level scheduled metric pullback dispatch queue."""

    try:
        response = await CommercialOperationService(session).get_metric_analysis_dispatch_queue(
            workspace_id=context.workspace_id,
            platform=platform,
            force=force,
            limit=limit,
        )
        return CommercialOperationMetricAnalysisDispatchQueueResponse(**response)
    except Exception as exc:
        logger.exception("Commercial operation metric analysis dispatch queue API failed")
        raise AppError("Commercial operation metric analysis dispatch queue failed", status_code=500) from exc


@router.get(
    "/production-closed-loop/intervention-queue",
    response_model=CommercialOperationProductionClosedLoopInterventionQueueResponse,
)
async def get_commercial_operation_production_closed_loop_intervention_queue(
    statuses: str = Query(default="stale,watch", description="Comma-separated staleness statuses, default stale,watch"),
    limit: int = Query(default=50, ge=1, le=100),
    scan_limit: int = Query(default=500, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopInterventionQueueResponse:
    """Read the workspace-level production closed-loop intervention queue."""

    try:
        service = CommercialOperationService(session)
        queue = await service.get_production_closed_loop_intervention_queue(
            workspace_id=context.workspace_id,
            statuses=[item.strip() for item in statuses.split(",") if item.strip()],
            limit=limit,
            scan_limit=scan_limit,
        )
        items: list[CommercialOperationProductionClosedLoopInterventionQueueItemResponse] = []
        for raw_item in queue["items"]:
            operation = raw_item["operation"]
            action_audit_summary = raw_item["action_audit_summary"]
            payload = {key: value for key, value in raw_item.items() if key != "operation"}
            items.append(
                CommercialOperationProductionClosedLoopInterventionQueueItemResponse(
                    **payload,
                    operation=CommercialOperationResponse.from_model(
                        operation,
                        production_closed_loop_action_audit_summary=action_audit_summary,
                    ),
                )
            )
        return CommercialOperationProductionClosedLoopInterventionQueueResponse(
            workspace_id=queue["workspace_id"],
            queue_status=queue["queue_status"],
            statuses=queue["statuses"],
            queue_count=queue["queue_count"],
            stale_count=queue["stale_count"],
            watch_count=queue["watch_count"],
            acknowledgement_sla_status_counts=queue["acknowledgement_sla_status_counts"],
            reminder_dispatch_status_counts=queue["reminder_dispatch_status_counts"],
            reminder_cooldown_status_counts=queue["reminder_cooldown_status_counts"],
            acknowledgement_overdue_count=queue["acknowledgement_overdue_count"],
            reminder_follow_up_count=queue["reminder_follow_up_count"],
            queue_summary=queue["queue_summary"],
            recommended_action=queue["recommended_action"],
            scanned_operation_count=queue["scanned_operation_count"],
            scan_limit=queue["scan_limit"],
            limit=queue["limit"],
            items=items,
            generated_at=queue["generated_at"],
            boundaries=queue["boundaries"],
            metadata=queue["metadata"],
        )
    except Exception as exc:
        logger.exception("Commercial operation production closed-loop intervention queue API failed")
        raise AppError("Commercial operation production closed-loop intervention queue failed", status_code=500) from exc


@router.get(
    "/production-closed-loop/acceptance-summary",
    response_model=CommercialOperationProductionClosedLoopAcceptanceSummaryResponse,
)
async def get_commercial_operation_production_closed_loop_acceptance_summary(
    platform: str | None = Query(default=None, description="Optional platform filter, for example douyin"),
    force_metric_due: bool = Query(default=False, description="Force metric dispatch due-state evaluation without mutating schedules"),
    limit: int = Query(default=25, ge=1, le=50),
    scan_limit: int = Query(default=50, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopAcceptanceSummaryResponse:
    """Read the workspace-level production closed-loop acceptance summary."""

    try:
        payload = await CommercialOperationService(session).get_production_closed_loop_acceptance_summary(
            workspace_id=context.workspace_id,
            platform=platform,
            force_metric_due=force_metric_due,
            limit=limit,
            scan_limit=scan_limit,
        )
        return CommercialOperationProductionClosedLoopAcceptanceSummaryResponse(**payload)
    except Exception as exc:
        logger.exception("Commercial operation production closed-loop acceptance summary API failed")
        raise AppError("Commercial operation production closed-loop acceptance summary failed", status_code=500) from exc


@router.get(
    "/production-closed-loop/delivery-plan",
    response_model=CommercialOperationProductionClosedLoopDeliveryPlanResponse,
)
async def get_commercial_operation_production_closed_loop_delivery_plan(
    platform: str | None = Query(default=None, description="Optional platform filter, for example douyin"),
    force_metric_due: bool = Query(default=False, description="Force metric dispatch due-state evaluation without mutating schedules"),
    limit: int = Query(default=25, ge=1, le=50),
    scan_limit: int = Query(default=50, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopDeliveryPlanResponse:
    """Read the workspace-level production closed-loop delivery plan."""

    try:
        payload = await CommercialOperationService(session).get_production_closed_loop_delivery_plan(
            workspace_id=context.workspace_id,
            platform=platform,
            force_metric_due=force_metric_due,
            limit=limit,
            scan_limit=scan_limit,
        )
        return CommercialOperationProductionClosedLoopDeliveryPlanResponse(**payload)
    except Exception as exc:
        logger.exception("Commercial operation production closed-loop delivery plan API failed")
        raise AppError("Commercial operation production closed-loop delivery plan failed", status_code=500) from exc


@router.get(
    "/production-closed-loop/delivery-audit/blocker-clearance-plan",
    response_model=CommercialOperationProductionClosedLoopDeliveryAuditBlockerClearancePlanResponse,
)
async def get_commercial_operation_production_closed_loop_delivery_audit_blocker_clearance_plan(
    platform: str | None = Query(default=None, description="Optional platform filter, for example douyin"),
    force_metric_due: bool = Query(default=False, description="Force metric dispatch due-state evaluation without mutating schedules"),
    limit: int = Query(default=25, ge=1, le=50),
    scan_limit: int = Query(default=50, ge=1, le=100),
    work_order_limit: int = Query(default=200, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopDeliveryAuditBlockerClearancePlanResponse:
    """Read production audit blockers mapped to clearance ownership and remediation work-order state."""

    try:
        payload = await CommercialOperationService(
            session
        ).get_production_closed_loop_delivery_audit_blocker_clearance_plan(
            workspace_id=context.workspace_id,
            platform=platform,
            force_metric_due=force_metric_due,
            limit=limit,
            scan_limit=scan_limit,
            work_order_limit=work_order_limit,
        )
        return CommercialOperationProductionClosedLoopDeliveryAuditBlockerClearancePlanResponse(**payload)
    except Exception as exc:
        logger.exception("Commercial operation production delivery audit blocker clearance plan API failed")
        raise AppError("Commercial operation production delivery audit blocker clearance plan failed", status_code=500) from exc


@router.post(
    "/production-closed-loop/delivery-audit/blocker-clearance-plan/assign-work-orders",
    response_model=CommercialOperationProductionClosedLoopDeliveryAuditBlockerWorkOrderAssignmentResponse,
    status_code=201,
)
async def assign_commercial_operation_production_closed_loop_delivery_audit_blocker_work_orders(
    request: CommercialOperationProductionClosedLoopDeliveryAuditBlockerWorkOrderAssignmentRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopDeliveryAuditBlockerWorkOrderAssignmentResponse:
    """Assign remediation work orders from production audit blocker clearance items."""

    try:
        payload = await CommercialOperationService(
            session
        ).assign_production_closed_loop_delivery_audit_blocker_clearance_work_orders(
            workspace_id=context.workspace_id,
            created_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationProductionClosedLoopDeliveryAuditBlockerWorkOrderAssignmentResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation production delivery audit blocker work-order assignment API failed")
        raise AppError(
            "Commercial operation production delivery audit blocker work-order assignment failed",
            status_code=500,
        ) from exc


@router.get(
    "/production-closed-loop/delivery-audit/blocker-runbook-packages",
    response_model=CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookPackageListResponse,
)
async def get_commercial_operation_production_closed_loop_delivery_audit_blocker_runbook_packages(
    platform: str | None = Query(default=None, description="Optional platform filter, for example douyin"),
    force_metric_due: bool = Query(default=False, description="Force metric dispatch due-state evaluation without mutating schedules"),
    limit: int = Query(default=25, ge=1, le=50),
    scan_limit: int = Query(default=50, ge=1, le=100),
    work_order_limit: int = Query(default=200, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookPackageListResponse:
    """Read runbook handoff packages for production audit blockers without executing them."""

    try:
        payload = await CommercialOperationService(
            session
        ).get_production_closed_loop_delivery_audit_blocker_runbook_packages(
            workspace_id=context.workspace_id,
            platform=platform,
            force_metric_due=force_metric_due,
            limit=limit,
            scan_limit=scan_limit,
            work_order_limit=work_order_limit,
        )
        return CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookPackageListResponse(**payload)
    except Exception as exc:
        logger.exception("Commercial operation production delivery audit blocker runbook packages API failed")
        raise AppError(
            "Commercial operation production delivery audit blocker runbook packages failed",
            status_code=500,
        ) from exc


@router.get(
    "/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-records",
    response_model=CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceListResponse,
)
async def list_commercial_operation_production_closed_loop_delivery_audit_blocker_runbook_evidence_records(
    package_key: str | None = Query(default=None, description="Optional runbook package key filter"),
    gate_key: str | None = Query(default=None, description="Optional delivery remediation gate filter"),
    operation_id: UUID | None = Query(default=None, description="Optional operation anchor filter"),
    evidence_status: str | None = Query(default=None, description="Optional evidence status filter"),
    limit: int = Query(default=50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceListResponse:
    """List runbook evidence records for production delivery audit blockers."""

    try:
        payload = await CommercialOperationService(
            session
        ).list_production_closed_loop_delivery_audit_blocker_runbook_evidence(
            workspace_id=context.workspace_id,
            package_key=package_key,
            gate_key=gate_key,
            operation_id=operation_id,
            evidence_status=evidence_status,
            limit=limit,
        )
        return CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceListResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation production delivery audit blocker runbook evidence list API failed")
        raise AppError(
            "Commercial operation production delivery audit blocker runbook evidence list failed",
            status_code=500,
        ) from exc


@router.post(
    "/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-records",
    response_model=CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceRecordResponse,
    status_code=201,
)
async def record_commercial_operation_production_closed_loop_delivery_audit_blocker_runbook_evidence(
    request: CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceRecordResponse:
    """Record operator evidence for a production delivery audit blocker runbook package."""

    try:
        payload = await CommercialOperationService(
            session
        ).record_production_closed_loop_delivery_audit_blocker_runbook_evidence(
            workspace_id=context.workspace_id,
            created_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceRecordResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation production delivery audit blocker runbook evidence record API failed")
        raise AppError(
            "Commercial operation production delivery audit blocker runbook evidence record failed",
            status_code=500,
        ) from exc


@router.get(
    "/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-coverage",
    response_model=CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverageResponse,
)
async def get_commercial_operation_production_closed_loop_delivery_audit_blocker_runbook_evidence_coverage(
    platform: str | None = Query(default=None, description="Optional platform filter, for example douyin"),
    force_metric_due: bool = Query(default=False, description="Force metric dispatch due-state evaluation without mutating schedules"),
    limit: int = Query(default=25, ge=1, le=50),
    scan_limit: int = Query(default=50, ge=1, le=100),
    work_order_limit: int = Query(default=200, ge=1, le=500),
    evidence_limit: int = Query(default=200, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverageResponse:
    """Read evidence coverage for production delivery audit blocker runbook packages."""

    try:
        payload = await CommercialOperationService(
            session
        ).get_production_closed_loop_delivery_audit_blocker_runbook_evidence_coverage(
            workspace_id=context.workspace_id,
            platform=platform,
            force_metric_due=force_metric_due,
            limit=limit,
            scan_limit=scan_limit,
            work_order_limit=work_order_limit,
            evidence_limit=evidence_limit,
        )
        return CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverageResponse(**payload)
    except Exception as exc:
        logger.exception("Commercial operation production delivery audit blocker runbook evidence coverage API failed")
        raise AppError(
            "Commercial operation production delivery audit blocker runbook evidence coverage failed",
            status_code=500,
        ) from exc


@router.post(
    "/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-coverage/readiness-refresh",
    response_model=CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceReadinessRefreshResponse,
)
async def refresh_commercial_operation_production_closed_loop_delivery_audit_blocker_runbook_evidence_readiness(
    request: CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceReadinessRefreshRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceReadinessRefreshResponse:
    """Refresh readiness after all delivery audit blocker runbook evidence is resolved."""

    try:
        payload = await CommercialOperationService(
            session
        ).refresh_production_closed_loop_delivery_audit_blocker_runbook_evidence_readiness(
            workspace_id=context.workspace_id,
            refreshed_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceReadinessRefreshResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation production delivery audit blocker runbook evidence readiness refresh API failed")
        raise AppError(
            "Commercial operation production delivery audit blocker runbook evidence readiness refresh failed",
            status_code=500,
        ) from exc


@router.get(
    "/production-closed-loop/delivery-audit/next-action-plan",
    response_model=CommercialOperationProductionClosedLoopDeliveryAuditNextActionPlanResponse,
)
async def get_commercial_operation_production_closed_loop_delivery_audit_next_action_plan(
    platform: str | None = Query(default=None, description="Optional platform filter, for example douyin"),
    force_metric_due: bool = Query(default=False, description="Force metric dispatch due-state evaluation without mutating schedules"),
    limit: int = Query(default=25, ge=1, le=50),
    scan_limit: int = Query(default=50, ge=1, le=100),
    work_order_limit: int = Query(default=200, ge=1, le=500),
    evidence_limit: int = Query(default=200, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopDeliveryAuditNextActionPlanResponse:
    """Read an owner-routed next-action plan for production delivery audit blockers."""

    try:
        payload = await CommercialOperationService(
            session
        ).get_production_closed_loop_delivery_audit_next_action_plan(
            workspace_id=context.workspace_id,
            platform=platform,
            force_metric_due=force_metric_due,
            limit=limit,
            scan_limit=scan_limit,
            work_order_limit=work_order_limit,
            evidence_limit=evidence_limit,
        )
        return CommercialOperationProductionClosedLoopDeliveryAuditNextActionPlanResponse(**payload)
    except Exception as exc:
        logger.exception("Commercial operation production delivery audit next action plan API failed")
        raise AppError(
            "Commercial operation production delivery audit next action plan failed",
            status_code=500,
        ) from exc


@router.get(
    "/production-closed-loop/delivery-audit/next-action-plan/operator-queue",
    response_model=CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueResponse,
)
async def get_commercial_operation_production_closed_loop_delivery_audit_operator_queue(
    platform: str | None = Query(default=None, description="Optional platform filter, for example douyin"),
    force_metric_due: bool = Query(default=False, description="Force metric dispatch due-state evaluation without mutating schedules"),
    limit: int = Query(default=25, ge=1, le=50),
    scan_limit: int = Query(default=50, ge=1, le=100),
    work_order_limit: int = Query(default=200, ge=1, le=500),
    evidence_limit: int = Query(default=200, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueResponse:
    """Read an owner-grouped operator queue for production delivery audit next actions."""

    try:
        payload = await CommercialOperationService(
            session
        ).get_production_closed_loop_delivery_audit_operator_queue(
            workspace_id=context.workspace_id,
            platform=platform,
            force_metric_due=force_metric_due,
            limit=limit,
            scan_limit=scan_limit,
            work_order_limit=work_order_limit,
            evidence_limit=evidence_limit,
        )
        return CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueResponse(**payload)
    except Exception as exc:
        logger.exception("Commercial operation production delivery audit operator queue API failed")
        raise AppError(
            "Commercial operation production delivery audit operator queue failed",
            status_code=500,
        ) from exc


@router.get(
    "/production-closed-loop/delivery-audit/next-action-plan/operator-queue/records",
    response_model=CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecordListResponse,
)
async def list_commercial_operation_production_closed_loop_delivery_audit_operator_queue_records(
    queue_key: str | None = Query(default=None, description="Optional operator queue key filter"),
    action_key: str | None = Query(default=None, description="Optional next-action key filter"),
    owner: str | None = Query(default=None, description="Optional queue owner filter"),
    operation_id: UUID | None = Query(default=None, description="Optional operation anchor filter"),
    record_status: str | None = Query(default=None, description="Optional queue record status filter"),
    limit: int = Query(default=50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecordListResponse:
    """List operator status/evidence records for production delivery audit queue items."""

    try:
        payload = await CommercialOperationService(
            session
        ).list_production_closed_loop_delivery_audit_operator_queue_records(
            workspace_id=context.workspace_id,
            queue_key=queue_key,
            action_key=action_key,
            owner=owner,
            operation_id=operation_id,
            record_status=record_status,
            limit=limit,
        )
        return CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecordListResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation production delivery audit operator queue record list API failed")
        raise AppError(
            "Commercial operation production delivery audit operator queue record list failed",
            status_code=500,
        ) from exc


@router.post(
    "/production-closed-loop/delivery-audit/next-action-plan/operator-queue/records",
    response_model=CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecordResponse,
    status_code=201,
)
async def record_commercial_operation_production_closed_loop_delivery_audit_operator_queue_record(
    request: CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecordRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecordResponse:
    """Record operator status/evidence for a production delivery audit queue item."""

    try:
        payload = await CommercialOperationService(
            session
        ).record_production_closed_loop_delivery_audit_operator_queue_record(
            workspace_id=context.workspace_id,
            created_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecordResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation production delivery audit operator queue record API failed")
        raise AppError(
            "Commercial operation production delivery audit operator queue record failed",
            status_code=500,
        ) from exc


@router.get(
    "/production-closed-loop/delivery-audit/openclaw-provider-handoff",
    response_model=CommercialOperationProductionClosedLoopDeliveryAuditOpenClawProviderHandoffResponse,
)
async def get_commercial_operation_production_closed_loop_delivery_audit_openclaw_provider_handoff(
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopDeliveryAuditOpenClawProviderHandoffResponse:
    """Read the sanitized real OpenClaw provider configuration handoff."""

    try:
        payload = await CommercialOperationService(
            session
        ).get_production_closed_loop_delivery_audit_openclaw_provider_handoff(
            workspace_id=context.workspace_id,
        )
        return CommercialOperationProductionClosedLoopDeliveryAuditOpenClawProviderHandoffResponse(**payload)
    except Exception as exc:
        logger.exception("Commercial operation production delivery audit OpenClaw provider handoff API failed")
        raise AppError(
            "Commercial operation production delivery audit OpenClaw provider handoff failed",
            status_code=500,
        ) from exc


@router.get(
    "/production-closed-loop/delivery-action-packages",
    response_model=CommercialOperationProductionClosedLoopDeliveryActionPackageListResponse,
)
async def get_commercial_operation_production_closed_loop_delivery_action_packages(
    platform: str | None = Query(default=None, description="Optional platform filter, for example douyin"),
    force_metric_due: bool = Query(default=False, description="Force metric dispatch due-state evaluation without mutating schedules"),
    limit: int = Query(default=25, ge=1, le=50),
    scan_limit: int = Query(default=50, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopDeliveryActionPackageListResponse:
    """Read manual action packages for open production closed-loop delivery gates."""

    try:
        payload = await CommercialOperationService(session).get_production_closed_loop_delivery_action_packages(
            workspace_id=context.workspace_id,
            platform=platform,
            force_metric_due=force_metric_due,
            limit=limit,
            scan_limit=scan_limit,
        )
        return CommercialOperationProductionClosedLoopDeliveryActionPackageListResponse(**payload)
    except Exception as exc:
        logger.exception("Commercial operation production closed-loop delivery action packages API failed")
        raise AppError("Commercial operation production closed-loop delivery action packages failed", status_code=500) from exc


@router.get(
    "/production-closed-loop/delivery-remediation-map",
    response_model=CommercialOperationProductionClosedLoopDeliveryRemediationMapResponse,
)
async def get_commercial_operation_production_closed_loop_delivery_remediation_map(
    platform: str | None = Query(default=None, description="Optional platform filter, for example douyin"),
    force_metric_due: bool = Query(default=False, description="Force metric dispatch due-state evaluation without mutating schedules"),
    limit: int = Query(default=25, ge=1, le=50),
    scan_limit: int = Query(default=50, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopDeliveryRemediationMapResponse:
    """Read remediation mappings for open production closed-loop delivery gates."""

    try:
        payload = await CommercialOperationService(session).get_production_closed_loop_delivery_remediation_map(
            workspace_id=context.workspace_id,
            platform=platform,
            force_metric_due=force_metric_due,
            limit=limit,
            scan_limit=scan_limit,
        )
        return CommercialOperationProductionClosedLoopDeliveryRemediationMapResponse(**payload)
    except Exception as exc:
        logger.exception("Commercial operation production closed-loop delivery remediation map API failed")
        raise AppError("Commercial operation production closed-loop delivery remediation map failed", status_code=500) from exc


@router.get(
    "/production-closed-loop/delivery-remediation-map/work-order-coverage",
    response_model=CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverageResponse,
)
async def get_commercial_operation_production_closed_loop_delivery_remediation_work_order_coverage(
    platform: str | None = Query(default=None, description="Optional platform filter"),
    force_metric_due: bool = Query(default=False, description="Treat metric feedback as due for readiness checks"),
    limit: int = Query(default=25, ge=1, le=50),
    scan_limit: int = Query(default=50, ge=1, le=100),
    work_order_limit: int = Query(default=200, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverageResponse:
    """Read remediation work-order ownership coverage for open production delivery gates."""

    try:
        payload = await CommercialOperationService(session).get_production_closed_loop_delivery_remediation_work_order_coverage(
            workspace_id=context.workspace_id,
            platform=platform,
            force_metric_due=force_metric_due,
            limit=limit,
            scan_limit=scan_limit,
            work_order_limit=work_order_limit,
        )
        return CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverageResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation production delivery remediation work-order coverage API failed")
        raise AppError("Commercial operation production delivery remediation work-order coverage failed", status_code=500) from exc


@router.post(
    "/production-closed-loop/delivery-remediation-map/work-order-coverage/assign-missing",
    response_model=CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderAssignmentResponse,
    status_code=201,
)
async def assign_missing_commercial_operation_production_closed_loop_delivery_remediation_work_orders(
    request: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderAssignmentRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderAssignmentResponse:
    """Assign work orders for currently unassigned delivery remediation items."""

    try:
        payload = await CommercialOperationService(session).assign_missing_production_closed_loop_delivery_remediation_work_orders(
            workspace_id=context.workspace_id,
            created_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderAssignmentResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation production delivery remediation work-order assignment API failed")
        raise AppError("Commercial operation production delivery remediation work-order assignment failed", status_code=500) from exc


@router.get(
    "/production-closed-loop/delivery-remediation-map/work-order-execution-prep",
    response_model=CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrepResponse,
)
async def get_commercial_operation_production_closed_loop_delivery_remediation_work_order_execution_prep(
    platform: str | None = Query(default=None, description="Optional platform filter"),
    force_metric_due: bool = Query(default=False, description="Treat metric feedback as due for readiness checks"),
    limit: int = Query(default=25, ge=1, le=50),
    scan_limit: int = Query(default=50, ge=1, le=100),
    work_order_limit: int = Query(default=200, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrepResponse:
    """Read execution-prep packages for delivery remediation work orders without executing target endpoints."""

    try:
        payload = await CommercialOperationService(
            session
        ).get_production_closed_loop_delivery_remediation_work_order_execution_prep(
            workspace_id=context.workspace_id,
            platform=platform,
            force_metric_due=force_metric_due,
            limit=limit,
            scan_limit=scan_limit,
            work_order_limit=work_order_limit,
        )
        return CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrepResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation production delivery remediation work-order execution prep API failed")
        raise AppError(
            "Commercial operation production delivery remediation work-order execution prep failed",
            status_code=500,
        ) from exc


@router.post(
    "/production-closed-loop/delivery-remediation-map/work-order-execution-prep/complete",
    response_model=CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCompletionResponse,
    status_code=201,
)
async def complete_commercial_operation_production_closed_loop_delivery_remediation_work_order(
    request: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCompletionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCompletionResponse:
    """Complete a delivery remediation work order from execution prep without executing target endpoints."""

    try:
        payload = await CommercialOperationService(session).complete_production_closed_loop_delivery_remediation_work_order(
            workspace_id=context.workspace_id,
            created_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCompletionResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation production delivery remediation work-order completion API failed")
        raise AppError(
            "Commercial operation production delivery remediation work-order completion failed",
            status_code=500,
        ) from exc


@router.post(
    "/production-closed-loop/delivery-remediation-map/work-order-completion/readiness-refresh",
    response_model=CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderReadinessRefreshResponse,
)
async def refresh_commercial_operation_production_closed_loop_delivery_remediation_work_order_readiness(
    request: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderReadinessRefreshRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderReadinessRefreshResponse:
    """Refresh readiness after completed delivery remediation work orders without external execution."""

    try:
        payload = await CommercialOperationService(
            session
        ).refresh_production_closed_loop_delivery_remediation_work_order_readiness(
            workspace_id=context.workspace_id,
            refreshed_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderReadinessRefreshResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation production delivery remediation work-order readiness refresh API failed")
        raise AppError(
            "Commercial operation production delivery remediation work-order readiness refresh failed",
            status_code=500,
        ) from exc


@router.get(
    "/production-closed-loop/delivery-remediation-map/work-orders",
    response_model=CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderListResponse,
)
async def list_commercial_operation_production_closed_loop_delivery_remediation_work_orders(
    gate_key: str | None = Query(default=None, description="Optional delivery remediation gate filter"),
    operation_id: UUID | None = Query(default=None, description="Optional operation anchor filter"),
    work_order_status: str | None = Query(default=None, description="Optional work-order status filter"),
    limit: int = Query(default=50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderListResponse:
    """List delivery remediation work-order records."""

    try:
        payload = await CommercialOperationService(session).list_production_closed_loop_delivery_remediation_work_orders(
            workspace_id=context.workspace_id,
            gate_key=gate_key,
            operation_id=operation_id,
            work_order_status=work_order_status,
            limit=limit,
        )
        return CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderListResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation production delivery remediation work-order list API failed")
        raise AppError("Commercial operation production delivery remediation work-order list failed", status_code=500) from exc


@router.post(
    "/production-closed-loop/delivery-remediation-map/work-orders",
    response_model=CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRecordResponse,
    status_code=201,
)
async def record_commercial_operation_production_closed_loop_delivery_remediation_work_order(
    request: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRecordResponse:
    """Record a delivery remediation work-order status without executing the remediation endpoint."""

    try:
        payload = await CommercialOperationService(session).record_production_closed_loop_delivery_remediation_work_order(
            workspace_id=context.workspace_id,
            created_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRecordResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation production delivery remediation work-order record API failed")
        raise AppError("Commercial operation production delivery remediation work-order record failed", status_code=500) from exc


@router.get(
    "/production-closed-loop/delivery-action-packages/evidence-records",
    response_model=CommercialOperationProductionClosedLoopDeliveryActionEvidenceListResponse,
)
async def list_commercial_operation_production_closed_loop_delivery_action_evidence_records(
    gate_key: str | None = Query(default=None, description="Optional delivery gate filter"),
    operation_id: UUID | None = Query(default=None, description="Optional operation anchor filter"),
    limit: int = Query(default=50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopDeliveryActionEvidenceListResponse:
    """List operator-supplied delivery action evidence records."""

    try:
        payload = await CommercialOperationService(session).list_production_closed_loop_delivery_action_evidence(
            workspace_id=context.workspace_id,
            gate_key=gate_key,
            operation_id=operation_id,
            limit=limit,
        )
        return CommercialOperationProductionClosedLoopDeliveryActionEvidenceListResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation production delivery action evidence list API failed")
        raise AppError("Commercial operation production delivery action evidence list failed", status_code=500) from exc


@router.post(
    "/production-closed-loop/delivery-action-packages/evidence-records",
    response_model=CommercialOperationProductionClosedLoopDeliveryActionEvidenceRecordResponse,
    status_code=201,
)
async def record_commercial_operation_production_closed_loop_delivery_action_evidence(
    request: CommercialOperationProductionClosedLoopDeliveryActionEvidenceRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopDeliveryActionEvidenceRecordResponse:
    """Record manual evidence for a delivery action package without executing the package endpoint."""

    try:
        payload = await CommercialOperationService(session).record_production_closed_loop_delivery_action_evidence(
            workspace_id=context.workspace_id,
            created_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationProductionClosedLoopDeliveryActionEvidenceRecordResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation production delivery action evidence record API failed")
        raise AppError("Commercial operation production delivery action evidence record failed", status_code=500) from exc


@router.get("/metric-analysis-dispatch/claims", response_model=CommercialOperationMetricDispatchClaimListResponse)
async def list_commercial_operation_metric_dispatch_claims(
    status: str | None = Query(default=None, description="claimed / running / completed / failed / released / expired"),
    limit: int = Query(default=50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMetricDispatchClaimListResponse:
    """List customer-machine metric dispatch claims for the current workspace."""

    try:
        response = await CommercialOperationService(session).list_metric_analysis_dispatch_claims(
            workspace_id=context.workspace_id,
            status=status,
            limit=limit,
        )
        return CommercialOperationMetricDispatchClaimListResponse(**response)
    except Exception as exc:
        logger.exception("Commercial operation metric dispatch claim list API failed")
        raise AppError("Commercial operation metric dispatch claim list failed", status_code=500) from exc


@router.post("/metric-analysis-dispatch/customer-poll", response_model=CommercialOperationMetricDispatchCustomerPollResponse)
async def poll_commercial_operation_metric_dispatch_for_customer_machine(
    request: CommercialOperationMetricDispatchCustomerPollRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMetricDispatchCustomerPollResponse:
    """Poll customer-machine metric dispatch state and optionally claim one task."""

    try:
        response = await CommercialOperationService(session).poll_metric_analysis_dispatch_for_customer_machine(
            workspace_id=context.workspace_id,
            platform=request.platform,
            force=request.force,
            collection_mode=request.collection_mode,
            customer_machine_id=request.customer_machine_id,
            auto_claim=request.auto_claim,
            operator_confirmed=request.operator_confirmed,
            lease_seconds=request.lease_seconds,
            target_operation_id=request.target_operation_id,
            limit=request.limit,
            metadata=request.metadata,
        )
        return CommercialOperationMetricDispatchCustomerPollResponse(**response)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Commercial operation customer-machine metric dispatch poll API failed")
        raise AppError("Commercial operation customer-machine metric dispatch poll failed", status_code=500) from exc


@router.post("/metric-analysis-dispatch/customer-poll/scheduler", response_model=CommercialOperationMetricDispatchPollSchedulerResponse)
async def schedule_commercial_operation_metric_dispatch_customer_poll(
    request: CommercialOperationMetricDispatchPollSchedulerRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMetricDispatchPollSchedulerResponse:
    """Build a customer-machine poll schedule and notification bridge payload."""

    try:
        response = await CommercialOperationService(session).schedule_metric_dispatch_customer_poll(
            workspace_id=context.workspace_id,
            platform=request.platform,
            force=request.force,
            collection_mode=request.collection_mode,
            customer_machine_id=request.customer_machine_id,
            scheduler_enabled=request.scheduler_enabled,
            auto_claim=request.auto_claim,
            operator_confirmed=request.operator_confirmed,
            requested_poll_interval_seconds=request.requested_poll_interval_seconds,
            lease_seconds=request.lease_seconds,
            target_operation_id=request.target_operation_id,
            limit=request.limit,
            run_poll_now=request.run_poll_now,
            notification_channels=request.notification_channels,
            notify_on=request.notify_on,
            metadata=request.metadata,
        )
        return CommercialOperationMetricDispatchPollSchedulerResponse(**response)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Commercial operation customer-machine metric dispatch scheduler API failed")
        raise AppError("Commercial operation customer-machine metric dispatch scheduler failed", status_code=500) from exc


@router.post("/metric-analysis-dispatch/claims", response_model=CommercialOperationMetricDispatchClaimResponse)
async def claim_commercial_operation_metric_dispatch(
    request: CommercialOperationMetricDispatchClaimRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMetricDispatchClaimResponse:
    """Claim one ready metric dispatch item for customer-machine execution."""

    try:
        response = await CommercialOperationService(session).claim_metric_analysis_dispatch(
            workspace_id=context.workspace_id,
            platform=request.platform,
            force=request.force,
            collection_mode=request.collection_mode,
            customer_machine_id=request.customer_machine_id,
            operator_confirmed=request.operator_confirmed,
            lease_seconds=request.lease_seconds,
            target_operation_id=request.target_operation_id,
            metadata=request.metadata,
        )
        return CommercialOperationMetricDispatchClaimResponse(**response)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Commercial operation metric dispatch claim API failed")
        raise AppError("Commercial operation metric dispatch claim failed", status_code=500) from exc


@router.post("/metric-analysis-dispatch/claims/{claim_id}/status", response_model=CommercialOperationMetricDispatchClaimResponse)
async def update_commercial_operation_metric_dispatch_claim_status(
    claim_id: UUID,
    request: CommercialOperationMetricDispatchClaimStatusRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMetricDispatchClaimResponse:
    """Update a customer-machine metric dispatch claim status."""

    try:
        response = await CommercialOperationService(session).update_metric_analysis_dispatch_claim(
            workspace_id=context.workspace_id,
            claim_id=claim_id,
            claim_status=request.claim_status,
            progress=request.progress,
            lease_seconds=request.lease_seconds,
            operator_notes=request.operator_notes,
            evidence_links=request.evidence_links,
            metadata=request.metadata,
        )
        return CommercialOperationMetricDispatchClaimResponse(**response)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404 if "not found" in str(exc).lower() else 400) from exc
    except Exception as exc:
        logger.exception("Commercial operation metric dispatch claim status API failed", extra={"claim_id": str(claim_id)})
        raise AppError("Commercial operation metric dispatch claim status failed", status_code=500) from exc


@router.get(
    "/{operation_id}/production-closed-loop/intervention-queue/acknowledgements",
    response_model=CommercialOperationProductionClosedLoopInterventionAcknowledgementListResponse,
)
async def list_commercial_operation_production_closed_loop_intervention_acknowledgements(
    operation_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopInterventionAcknowledgementListResponse:
    """List intervention queue acknowledgement records for one operation."""

    try:
        payload = await CommercialOperationService(session).list_production_closed_loop_intervention_acknowledgements(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
        )
        records = [
            CommercialOperationProductionClosedLoopInterventionAcknowledgementResponse(**record)
            for record in payload["records"]
        ]
        return CommercialOperationProductionClosedLoopInterventionAcknowledgementListResponse(
            operation_id=payload["operation_id"],
            workspace_id=payload["workspace_id"],
            acknowledgement_count=payload["acknowledgement_count"],
            latest_record=records[-1] if records else None,
            records=records,
            generated_at=payload["generated_at"],
            boundaries=payload["boundaries"],
            metadata=payload["metadata"],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation production closed-loop intervention acknowledgement list API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation production closed-loop intervention acknowledgement list failed", status_code=500) from exc


@router.post(
    "/{operation_id}/production-closed-loop/intervention-queue/acknowledgements",
    response_model=CommercialOperationProductionClosedLoopInterventionAcknowledgementResponse,
    status_code=201,
)
async def record_commercial_operation_production_closed_loop_intervention_acknowledgement(
    operation_id: UUID,
    request: CommercialOperationProductionClosedLoopInterventionAcknowledgementRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopInterventionAcknowledgementResponse:
    """Record operator ownership for one intervention queue item without executing it."""

    try:
        payload = await CommercialOperationService(session).record_production_closed_loop_intervention_acknowledgement(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            acknowledgement_status=request.acknowledgement_status,
            assignee=request.assignee,
            operator_confirmed=request.operator_confirmed,
            acknowledgement_notes=request.acknowledgement_notes,
            created_by=context.user_id,
            metadata=request.metadata,
        )
        return CommercialOperationProductionClosedLoopInterventionAcknowledgementResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation production closed-loop intervention acknowledgement API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation production closed-loop intervention acknowledgement failed", status_code=500) from exc


@router.get(
    "/{operation_id}/production-closed-loop/intervention-queue/reminder-dispatches",
    response_model=CommercialOperationProductionClosedLoopInterventionReminderDispatchListResponse,
)
async def list_commercial_operation_production_closed_loop_intervention_reminder_dispatches(
    operation_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopInterventionReminderDispatchListResponse:
    """List reminder dispatch records for one intervention queue item."""

    try:
        payload = await CommercialOperationService(session).list_production_closed_loop_intervention_reminder_dispatches(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
        )
        records = [
            CommercialOperationProductionClosedLoopInterventionReminderDispatchResponse(**record)
            for record in payload["records"]
        ]
        return CommercialOperationProductionClosedLoopInterventionReminderDispatchListResponse(
            operation_id=payload["operation_id"],
            workspace_id=payload["workspace_id"],
            reminder_dispatch_count=payload["reminder_dispatch_count"],
            latest_record=records[-1] if records else None,
            records=records,
            generated_at=payload["generated_at"],
            boundaries=payload["boundaries"],
            metadata=payload["metadata"],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation production closed-loop intervention reminder dispatch list API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation production closed-loop intervention reminder dispatch list failed", status_code=500) from exc


@router.post(
    "/{operation_id}/production-closed-loop/intervention-queue/reminder-dispatches",
    response_model=CommercialOperationProductionClosedLoopInterventionReminderDispatchResponse,
    status_code=201,
)
async def record_commercial_operation_production_closed_loop_intervention_reminder_dispatch(
    operation_id: UUID,
    request: CommercialOperationProductionClosedLoopInterventionReminderDispatchRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopInterventionReminderDispatchResponse:
    """Record a safe reminder dispatch without sending it automatically."""

    try:
        payload = await CommercialOperationService(session).record_production_closed_loop_intervention_reminder_dispatch(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            reminder_status=request.reminder_status,
            reminder_channel=request.reminder_channel,
            reminder_recipient=request.reminder_recipient,
            reminder_message=request.reminder_message,
            operator_confirmed=request.operator_confirmed,
            evidence_links=request.evidence_links,
            dispatch_notes=request.dispatch_notes,
            created_by=context.user_id,
            metadata=request.metadata,
        )
        return CommercialOperationProductionClosedLoopInterventionReminderDispatchResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation production closed-loop intervention reminder dispatch API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation production closed-loop intervention reminder dispatch failed", status_code=500) from exc


@router.get("/{operation_id}", response_model=CommercialOperationResponse)
async def get_commercial_operation(
    operation_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationResponse:
    """Read one commercial operation in the current workspace."""

    try:
        operation = await CommercialOperationService(session).require_operation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
        )
        return CommercialOperationResponse.from_model(operation)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation get API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation get failed", status_code=500) from exc


@router.patch("/{operation_id}", response_model=CommercialOperationResponse)
async def update_commercial_operation(
    operation_id: UUID,
    request: CommercialOperationUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationResponse:
    """Patch one commercial operation and rebuild its non-executing plan outline."""

    try:
        operation = await CommercialOperationService(session).update_operation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            patch=request.model_dump(exclude_unset=True),
        )
        return CommercialOperationResponse.from_model(operation)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception("Commercial operation update API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation update failed", status_code=500) from exc


@router.delete("/{operation_id}", response_model=CommercialOperationResponse)
async def delete_commercial_operation(
    operation_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationResponse:
    """Archive one commercial operation so it disappears from the default project list."""

    try:
        operation = await CommercialOperationService(session).archive_operation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            actor_user_id=context.user_id,
        )
        return CommercialOperationResponse.from_model(operation)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation delete API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation delete failed", status_code=500) from exc


@router.post("/{operation_id}/plan-draft", response_model=CommercialOperationPlanPreviewResponse)
async def regenerate_commercial_operation_plan(
    operation_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationPlanPreviewResponse:
    """Regenerate the conservative plan outline without executing external actions."""

    try:
        operation = await CommercialOperationService(session).regenerate_plan(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
        )
        return CommercialOperationPlanPreviewResponse(
            operation_id=operation.id,
            plan_outline=operation.plan_outline,
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation plan API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation plan failed", status_code=500) from exc


@router.get("/{operation_id}/operation-loop", response_model=CommercialOperationLoopSummaryResponse)
async def get_commercial_operation_loop_summary(
    operation_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationLoopSummaryResponse:
    """Read the operation-loop protocol for server and customer-machine consoles."""

    try:
        payload = await CommercialOperationService(session).get_operation_loop_summary(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
        )
        return CommercialOperationLoopSummaryResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation loop API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation loop failed", status_code=500) from exc


@router.get(
    "/{operation_id}/production-closed-loop/readiness",
    response_model=CommercialOperationProductionClosedLoopReadinessResponse,
)
async def get_commercial_operation_production_closed_loop_readiness(
    operation_id: UUID,
    platform: str | None = Query(default=None, description="Optional platform filter, for example douyin"),
    force_metric_due: bool = Query(default=False, description="Force metric dispatch due-state evaluation without mutating schedules"),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopReadinessResponse:
    """Read the production E2E readiness state across project, output, publish, and metric feedback."""

    try:
        payload = await CommercialOperationService(session).get_production_closed_loop_readiness(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            platform=platform,
            force_metric_due=force_metric_due,
        )
        return CommercialOperationProductionClosedLoopReadinessResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation production closed-loop readiness API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation production closed-loop readiness failed", status_code=500) from exc


@router.get(
    "/{operation_id}/production-closed-loop/next-action",
    response_model=CommercialOperationProductionClosedLoopNextActionResponse,
)
async def get_commercial_operation_production_closed_loop_next_action(
    operation_id: UUID,
    platform: str | None = Query(default=None, description="Optional platform filter, for example douyin"),
    force_metric_due: bool = Query(default=False, description="Force metric dispatch due-state evaluation without mutating schedules"),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopNextActionResponse:
    """Read the controlled next-action contract derived from production E2E readiness."""

    try:
        payload = await CommercialOperationService(session).get_production_closed_loop_next_action(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            platform=platform,
            force_metric_due=force_metric_due,
        )
        return CommercialOperationProductionClosedLoopNextActionResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation production closed-loop next-action API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation production closed-loop next-action failed", status_code=500) from exc


@router.post(
    "/{operation_id}/production-closed-loop/next-cycle-draft",
    response_model=CommercialOperationNextCycleDraftResponse,
    status_code=201,
)
async def prepare_commercial_operation_production_closed_loop_next_cycle_draft(
    operation_id: UUID,
    request: CommercialOperationNextCycleDraftRequest,
    platform: str | None = Query(default=None, description="Optional platform filter, for example douyin"),
    force_metric_due: bool = Query(default=True, description="Force metric dispatch due-state evaluation before drafting"),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationNextCycleDraftResponse:
    """Create a reviewable next-cycle operation plan and production-task draft package."""

    try:
        payload = await CommercialOperationService(session).prepare_next_operation_cycle(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            actor_user_id=context.user_id,
            operator_confirmed=request.operator_confirmed,
            source_decision_id=request.source_decision_id,
            create_tasks=request.create_tasks,
            operator_note=request.operator_note,
            metadata=request.metadata,
            platform=platform,
            force_metric_due=force_metric_due,
        )
        return CommercialOperationNextCycleDraftResponse(
            operation_id=payload["operation_id"],
            workspace_id=payload["workspace_id"],
            draft_status=payload["draft_status"],
            source_decision_id=payload["source_decision"].id,
            operation_plan=CommercialOperationPlanResponse.from_model(payload["operation_plan"]),
            production_tasks=[
                CommercialOperationProductionTaskResponse.from_model(task)
                for task in payload.get("production_tasks", [])
            ],
            readiness_status_before=payload.get("readiness_status_before"),
            next_action_key_before=payload.get("next_action_key_before"),
            operator_next_actions=payload.get("operator_next_actions", []),
            server_next_actions=payload.get("server_next_actions", []),
            client_next_actions=payload.get("client_next_actions", []),
            boundaries=payload.get("boundaries", []),
            metadata=payload.get("metadata", {}),
            generated_at=payload["generated_at"],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation production closed-loop next-cycle draft API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation production closed-loop next-cycle draft failed", status_code=500) from exc


@router.get(
    "/{operation_id}/production-closed-loop/next-action/audit-records",
    response_model=CommercialOperationProductionClosedLoopActionAuditListResponse,
)
async def list_commercial_operation_production_closed_loop_action_audits(
    operation_id: UUID,
    limit: int = Query(default=20, ge=1, le=100, description="Maximum audit records to return"),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopActionAuditListResponse:
    """Read metadata-only audit records for controlled production next actions."""

    try:
        payload = await CommercialOperationService(session).list_production_closed_loop_action_audits(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            limit=limit,
        )
        return CommercialOperationProductionClosedLoopActionAuditListResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation production closed-loop action audit list API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation production closed-loop action audit list failed", status_code=500) from exc


@router.post(
    "/{operation_id}/production-closed-loop/next-action/audit-records",
    response_model=CommercialOperationProductionClosedLoopActionAuditRecordResponse,
    status_code=201,
)
async def create_commercial_operation_production_closed_loop_action_audit(
    operation_id: UUID,
    request: CommercialOperationProductionClosedLoopActionAuditCreateRequest,
    platform: str | None = Query(default=None, description="Optional platform filter, for example douyin"),
    force_metric_due: bool = Query(default=False, description="Force metric dispatch due-state evaluation without mutating schedules"),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopActionAuditRecordResponse:
    """Record operator confirmation/evidence for the controlled next-action contract without executing it."""

    try:
        payload = await CommercialOperationService(session).record_production_closed_loop_action_audit(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            created_by=context.user_id,
            platform=platform,
            force_metric_due=force_metric_due,
            **request.model_dump(),
        )
        return CommercialOperationProductionClosedLoopActionAuditRecordResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation production closed-loop action audit create API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation production closed-loop action audit create failed", status_code=500) from exc


@router.post(
    "/{operation_id}/production-closed-loop/next-action/audit-records/{audit_id}/result-binding",
    response_model=CommercialOperationProductionClosedLoopActionResultBindingResponse,
    status_code=201,
)
async def bind_commercial_operation_production_closed_loop_action_result(
    operation_id: UUID,
    audit_id: UUID,
    request: CommercialOperationProductionClosedLoopActionResultBindingRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopActionResultBindingResponse:
    """Bind a controlled action audit event to the returned business result without executing the action."""

    try:
        payload = await CommercialOperationService(session).bind_production_closed_loop_action_result(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            audit_id=audit_id,
            bound_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationProductionClosedLoopActionResultBindingResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation production closed-loop action result binding API failed",
            extra={"operation_id": str(operation_id), "audit_id": str(audit_id)},
        )
        raise AppError("Commercial operation production closed-loop action result binding failed", status_code=500) from exc


@router.post(
    "/{operation_id}/production-closed-loop/next-action/audit-records/{audit_id}/result-binding/readiness-refresh",
    response_model=CommercialOperationProductionClosedLoopActionReadinessRefreshResponse,
)
async def refresh_commercial_operation_production_closed_loop_action_result_readiness(
    operation_id: UUID,
    audit_id: UUID,
    request: CommercialOperationProductionClosedLoopActionReadinessRefreshRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopActionReadinessRefreshResponse:
    """Refresh readiness after a controlled action result binding without executing the next action."""

    try:
        payload = await CommercialOperationService(session).refresh_production_closed_loop_action_result_readiness(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            audit_id=audit_id,
            refreshed_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationProductionClosedLoopActionReadinessRefreshResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation production closed-loop action result readiness refresh API failed",
            extra={"operation_id": str(operation_id), "audit_id": str(audit_id)},
        )
        raise AppError("Commercial operation production closed-loop action result readiness refresh failed", status_code=500) from exc


@router.post(
    "/{operation_id}/production-closed-loop/next-action/audit-records/{audit_id}/result-binding/record-validation",
    response_model=CommercialOperationProductionClosedLoopActionResultRecordValidationResponse,
)
async def validate_commercial_operation_production_closed_loop_action_result_record(
    operation_id: UUID,
    audit_id: UUID,
    request: CommercialOperationProductionClosedLoopActionResultRecordValidationRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionClosedLoopActionResultRecordValidationResponse:
    """Validate that a controlled action result binding points to a real project record without mutating that record."""

    try:
        payload = await CommercialOperationService(session).validate_production_closed_loop_action_result_record(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            audit_id=audit_id,
            validated_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationProductionClosedLoopActionResultRecordValidationResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation production closed-loop action result record validation API failed",
            extra={"operation_id": str(operation_id), "audit_id": str(audit_id)},
        )
        raise AppError("Commercial operation production closed-loop action result record validation failed", status_code=500) from exc


@router.post("/{operation_id}/operation-plans", response_model=CommercialOperationPlanResponse, status_code=201)
async def create_commercial_operation_plan(
    operation_id: UUID,
    request: CommercialOperationPlanCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationPlanResponse:
    """Create a first-class, approval-ready operation plan record."""

    try:
        plan = await CommercialOperationService(session).create_operation_plan(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            created_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationPlanResponse.from_model(plan)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation plan create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation plan create failed", status_code=500) from exc


@router.get("/{operation_id}/operation-plans", response_model=CommercialOperationPlanListResponse)
async def list_commercial_operation_plans(
    operation_id: UUID,
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationPlanListResponse:
    """List first-class operation plans for one operation."""

    try:
        plans = await CommercialOperationService(session).list_operation_plans(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            limit=limit,
        )
        return CommercialOperationPlanListResponse(
            operation_id=operation_id,
            items=[CommercialOperationPlanResponse.from_model(plan) for plan in plans],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation plan list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation plan list failed", status_code=500) from exc


@router.post("/{operation_id}/operation-plans/{plan_id}/{action}", response_model=CommercialOperationPlanResponse)
async def decide_commercial_operation_plan(
    operation_id: UUID,
    plan_id: UUID,
    action: str,
    request: CommercialOperationProjectDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationPlanResponse:
    """Move an operation plan through ready/approve/reject/archive states."""

    status_by_action = {
        "ready": "ready_for_review",
        "approve": "approved",
        "reject": "rejected",
        "archive": "archived",
    }
    if action not in status_by_action:
        raise AppError("Unsupported operation plan action", status_code=400)
    try:
        service = CommercialOperationService(session)
        plan = await service.set_operation_plan_status(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            plan_id=plan_id,
            status=status_by_action[action],
            actor_user_id=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        if action == "approve":
            await service.advance_main_agent_loop(
                workspace_id=context.workspace_id,
                operation_id=operation_id,
                actor_user_id=context.user_id,
                operator_note="Approved operation plan; derive reviewable implementation tasks for the next layer.",
                metadata={
                    "source": "operation_plan_approval_route",
                    "approved_operation_plan_id": str(plan.id),
                    "enter_implementation_after_plan_approval": True,
                },
            )
        return CommercialOperationPlanResponse.from_model(plan)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation plan decision API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation plan decision failed", status_code=500) from exc


@router.post("/{operation_id}/project-materials", response_model=CommercialOperationProjectMaterialResponse, status_code=201)
async def create_commercial_operation_project_material(
    operation_id: UUID,
    request: CommercialOperationProjectMaterialCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProjectMaterialResponse:
    """Register project-scoped material imported from a customer machine or server operator."""

    try:
        material = await CommercialOperationService(session).create_project_material(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            uploaded_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationProjectMaterialResponse.from_model(material)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation project material create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation project material create failed", status_code=500) from exc


@router.get("/{operation_id}/project-materials", response_model=CommercialOperationProjectMaterialListResponse)
async def list_commercial_operation_project_materials(
    operation_id: UUID,
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProjectMaterialListResponse:
    """List project-scoped materials."""

    try:
        materials = await CommercialOperationService(session).list_project_materials(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            limit=limit,
        )
        return CommercialOperationProjectMaterialListResponse(
            operation_id=operation_id,
            items=[CommercialOperationProjectMaterialResponse.from_model(material) for material in materials],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation project material list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation project material list failed", status_code=500) from exc


@router.post("/{operation_id}/project-materials/{material_id}/{action}", response_model=CommercialOperationProjectMaterialResponse)
async def decide_commercial_operation_project_material(
    operation_id: UUID,
    material_id: UUID,
    action: str,
    request: CommercialOperationProjectDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProjectMaterialResponse:
    """Ready, approve, reject, or archive a project material."""

    status_by_action = {"ready": "ready_for_review", "approve": "approved", "reject": "rejected", "archive": "archived"}
    if action not in status_by_action:
        raise AppError("Unsupported project material action", status_code=400)
    try:
        material = await CommercialOperationService(session).set_project_material_status(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            material_id=material_id,
            status=status_by_action[action],
            actor_user_id=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationProjectMaterialResponse.from_model(material)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation project material decision API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation project material decision failed", status_code=500) from exc


@router.post("/{operation_id}/production-tasks", response_model=CommercialOperationProductionTaskResponse, status_code=201)
async def create_commercial_operation_production_task(
    operation_id: UUID,
    request: CommercialOperationProductionTaskCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionTaskResponse:
    """Create a copy, image, or media production task."""

    try:
        task = await CommercialOperationService(session).create_production_task(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            created_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationProductionTaskResponse.from_model(task)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation production task create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation production task create failed", status_code=500) from exc


@router.get("/{operation_id}/production-tasks", response_model=CommercialOperationProductionTaskListResponse)
async def list_commercial_operation_production_tasks(
    operation_id: UUID,
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionTaskListResponse:
    """List project production tasks."""

    try:
        tasks = await CommercialOperationService(session).list_production_tasks(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            limit=limit,
        )
        return CommercialOperationProductionTaskListResponse(
            operation_id=operation_id,
            items=[CommercialOperationProductionTaskResponse.from_model(task) for task in tasks],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation production task list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation production task list failed", status_code=500) from exc


@router.post("/{operation_id}/production-tasks/{production_task_id}/{action}", response_model=CommercialOperationProductionTaskResponse)
async def decide_commercial_operation_production_task(
    operation_id: UUID,
    production_task_id: UUID,
    action: str,
    request: CommercialOperationProjectDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationProductionTaskResponse:
    """Move a production task through review and execution-prep states."""

    status_by_action = {
        "ready": "ready_for_review",
        "approve": "approved",
        "start": "in_progress",
        "block": "blocked",
        "complete": "completed",
        "reject": "rejected",
        "archive": "archived",
    }
    if action not in status_by_action:
        raise AppError("Unsupported production task action", status_code=400)
    try:
        task = await CommercialOperationService(session).set_production_task_status(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            production_task_id=production_task_id,
            status=status_by_action[action],
            actor_user_id=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationProductionTaskResponse.from_model(task)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation production task decision API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation production task decision failed", status_code=500) from exc


@router.get(
    "/{operation_id}/production-tasks/{production_task_id}/workflow-candidates",
    response_model=CommercialOperationWorkflowCandidateListResponse,
)
async def list_commercial_operation_workflow_candidates(
    operation_id: UUID,
    production_task_id: UUID,
    limit: int = Query(default=8, ge=1, le=20),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationWorkflowCandidateListResponse:
    """List library-backed workflow candidates for a production task."""

    try:
        response = await CommercialOperationService(session).list_workflow_candidates(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            production_task_id=production_task_id,
            limit=limit,
        )
        return CommercialOperationWorkflowCandidateListResponse(**response)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation workflow candidate API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation workflow candidate list failed", status_code=500) from exc


@router.post("/{operation_id}/workflow-selections", response_model=CommercialOperationWorkflowSelectionResponse, status_code=201)
async def create_commercial_operation_workflow_selection(
    operation_id: UUID,
    request: CommercialOperationWorkflowSelectionCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationWorkflowSelectionResponse:
    """Create an agent-recommended, human-confirmable workflow selection."""

    try:
        selection = await CommercialOperationService(session).create_workflow_selection(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            selected_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationWorkflowSelectionResponse.from_model(selection)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation workflow selection create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation workflow selection create failed", status_code=500) from exc


@router.get("/{operation_id}/workflow-selections", response_model=CommercialOperationWorkflowSelectionListResponse)
async def list_commercial_operation_workflow_selections(
    operation_id: UUID,
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationWorkflowSelectionListResponse:
    """List workflow selections for customer-machine confirmation."""

    try:
        selections = await CommercialOperationService(session).list_workflow_selections(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            limit=limit,
        )
        return CommercialOperationWorkflowSelectionListResponse(
            operation_id=operation_id,
            items=[CommercialOperationWorkflowSelectionResponse.from_model(selection) for selection in selections],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation workflow selection list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation workflow selection list failed", status_code=500) from exc


@router.post("/{operation_id}/workflow-selections/{workflow_selection_id}/{action}", response_model=CommercialOperationWorkflowSelectionResponse)
async def decide_commercial_operation_workflow_selection(
    operation_id: UUID,
    workflow_selection_id: UUID,
    action: str,
    request: CommercialOperationProjectDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationWorkflowSelectionResponse:
    """Ready, approve, reject, or archive a workflow selection."""

    status_by_action = {"ready": "ready_for_review", "approve": "approved", "reject": "rejected", "archive": "archived"}
    if action not in status_by_action:
        raise AppError("Unsupported workflow selection action", status_code=400)
    try:
        selection = await CommercialOperationService(session).set_workflow_selection_status(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            workflow_selection_id=workflow_selection_id,
            status=status_by_action[action],
            actor_user_id=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationWorkflowSelectionResponse.from_model(selection)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation workflow selection decision API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation workflow selection decision failed", status_code=500) from exc


@router.post("/{operation_id}/output-candidates", response_model=CommercialOperationOutputCandidateResponse, status_code=201)
async def create_commercial_operation_output_candidate(
    operation_id: UUID,
    request: CommercialOperationOutputCandidateCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationOutputCandidateResponse:
    """Register a generated output candidate for customer-machine preview."""

    try:
        candidate = await CommercialOperationService(session).create_output_candidate(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            created_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationOutputCandidateResponse.from_model(candidate)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation output candidate create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation output candidate create failed", status_code=500) from exc


@router.get("/{operation_id}/output-candidates", response_model=CommercialOperationOutputCandidateListResponse)
async def list_commercial_operation_output_candidates(
    operation_id: UUID,
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationOutputCandidateListResponse:
    """List generated output candidates."""

    try:
        candidates = await CommercialOperationService(session).list_output_candidates(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            limit=limit,
        )
        return CommercialOperationOutputCandidateListResponse(
            operation_id=operation_id,
            items=[CommercialOperationOutputCandidateResponse.from_model(candidate) for candidate in candidates],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation output candidate list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation output candidate list failed", status_code=500) from exc


@router.post("/{operation_id}/output-candidates/{output_candidate_id}/{action}", response_model=CommercialOperationOutputCandidateResponse)
async def decide_commercial_operation_output_candidate(
    operation_id: UUID,
    output_candidate_id: UUID,
    action: str,
    request: CommercialOperationProjectDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationOutputCandidateResponse:
    """Mark a generated candidate ready, selected, rejected, or archived."""

    status_by_action = {"ready": "ready_for_review", "select": "selected", "reject": "rejected", "archive": "archived"}
    if action not in status_by_action:
        raise AppError("Unsupported output candidate action", status_code=400)
    try:
        candidate = await CommercialOperationService(session).set_output_candidate_status(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            output_candidate_id=output_candidate_id,
            status=status_by_action[action],
            actor_user_id=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationOutputCandidateResponse.from_model(candidate)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation output candidate decision API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation output candidate decision failed", status_code=500) from exc


@router.get(
    "/{operation_id}/production-tasks/{production_task_id}/output-prep-package",
    response_model=CommercialOperationOutputPrepPackageResponse,
)
async def get_commercial_operation_output_prep_package(
    operation_id: UUID,
    production_task_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationOutputPrepPackageResponse:
    """Build a read-only package for registering output candidates."""

    try:
        response = await CommercialOperationService(session).get_output_prep_package(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            production_task_id=production_task_id,
        )
        return CommercialOperationOutputPrepPackageResponse(**response)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation output prep package API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation output prep package failed", status_code=500) from exc


@router.post("/{operation_id}/final-selections", response_model=CommercialOperationFinalSelectionResponse, status_code=201)
async def create_commercial_operation_final_selection(
    operation_id: UUID,
    request: CommercialOperationFinalSelectionCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationFinalSelectionResponse:
    """Create a final human selection from a previewed output candidate."""

    try:
        selection = await CommercialOperationService(session).create_final_selection(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            selected_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationFinalSelectionResponse.from_model(selection)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation final selection create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation final selection create failed", status_code=500) from exc


@router.get("/{operation_id}/final-selections", response_model=CommercialOperationFinalSelectionListResponse)
async def list_commercial_operation_final_selections(
    operation_id: UUID,
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationFinalSelectionListResponse:
    """List final selections for one operation."""

    try:
        selections = await CommercialOperationService(session).list_final_selections(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            limit=limit,
        )
        return CommercialOperationFinalSelectionListResponse(
            operation_id=operation_id,
            items=[CommercialOperationFinalSelectionResponse.from_model(selection) for selection in selections],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation final selection list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation final selection list failed", status_code=500) from exc


@router.post("/{operation_id}/final-selections/{final_selection_id}/{action}", response_model=CommercialOperationFinalSelectionResponse)
async def decide_commercial_operation_final_selection(
    operation_id: UUID,
    final_selection_id: UUID,
    action: str,
    request: CommercialOperationProjectDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationFinalSelectionResponse:
    """Ready, approve, reject, or archive a final output selection."""

    status_by_action = {"ready": "ready_for_review", "approve": "approved", "reject": "rejected", "archive": "archived"}
    if action not in status_by_action:
        raise AppError("Unsupported final selection action", status_code=400)
    try:
        selection = await CommercialOperationService(session).set_final_selection_status(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            final_selection_id=final_selection_id,
            status=status_by_action[action],
            actor_user_id=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationFinalSelectionResponse.from_model(selection)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation final selection decision API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation final selection decision failed", status_code=500) from exc


@router.get(
    "/{operation_id}/final-selections/{final_selection_id}/publish-prep-package",
    response_model=CommercialOperationPublishPrepPackageResponse,
)
async def get_commercial_operation_publish_prep_package(
    operation_id: UUID,
    final_selection_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationPublishPrepPackageResponse:
    """Build a read-only package for preparing platform publish packages."""

    try:
        response = await CommercialOperationService(session).get_publish_prep_package(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            final_selection_id=final_selection_id,
        )
        return CommercialOperationPublishPrepPackageResponse(**response)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation publish prep package API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation publish prep package failed", status_code=500) from exc


@router.post("/{operation_id}/publish-packages", response_model=CommercialOperationPublishPackageResponse, status_code=201)
async def create_commercial_operation_publish_package(
    operation_id: UUID,
    request: CommercialOperationPublishPackageCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationPublishPackageResponse:
    """Create a platform-specific publish package awaiting approval."""

    try:
        package = await CommercialOperationService(session).create_publish_package(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            created_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationPublishPackageResponse.from_model(package)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation publish package create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation publish package create failed", status_code=500) from exc


@router.get("/{operation_id}/publish-packages", response_model=CommercialOperationPublishPackageListResponse)
async def list_commercial_operation_publish_packages(
    operation_id: UUID,
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationPublishPackageListResponse:
    """List publish packages."""

    try:
        packages = await CommercialOperationService(session).list_publish_packages(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            limit=limit,
        )
        return CommercialOperationPublishPackageListResponse(
            operation_id=operation_id,
            items=[CommercialOperationPublishPackageResponse.from_model(package) for package in packages],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation publish package list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation publish package list failed", status_code=500) from exc


@router.post(
    "/{operation_id}/publish-packages/{publish_package_id}/execution-result",
    response_model=CommercialOperationPublishExecutionResultResponse,
    status_code=201,
)
async def capture_commercial_operation_publish_execution_result(
    operation_id: UUID,
    publish_package_id: UUID,
    request: CommercialOperationPublishExecutionResultCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationPublishExecutionResultResponse:
    """Capture customer-machine publish execution result evidence for a prepared publish package."""

    try:
        response = await CommercialOperationService(session).capture_publish_execution_result(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            publish_package_id=publish_package_id,
            actor_user_id=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationPublishExecutionResultResponse(**response)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation publish execution result API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation publish execution result failed", status_code=500) from exc


@router.post(
    "/{operation_id}/publish-packages/{publish_package_id}/execution-status",
    response_model=CommercialOperationPublishExecutionStatusResponse,
)
async def update_commercial_operation_publish_execution_status(
    operation_id: UUID,
    publish_package_id: UUID,
    request: CommercialOperationPublishExecutionStatusUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationPublishExecutionStatusResponse:
    """Update customer-machine publish execution progress before final result capture."""

    try:
        response = await CommercialOperationService(session).update_publish_execution_status(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            publish_package_id=publish_package_id,
            actor_user_id=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationPublishExecutionStatusResponse(**response)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation publish execution status API failed",
            extra={"operation_id": str(operation_id), "publish_package_id": str(publish_package_id)},
        )
        raise AppError("Commercial operation publish execution status failed", status_code=500) from exc


@router.post("/{operation_id}/publish-packages/{publish_package_id}/{action}", response_model=CommercialOperationPublishPackageResponse)
async def decide_commercial_operation_publish_package(
    operation_id: UUID,
    publish_package_id: UUID,
    action: str,
    request: CommercialOperationProjectDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationPublishPackageResponse:
    """Move a publish package through review, preparation, publish, or failure states."""

    status_by_action = {
        "ready": "ready_for_review",
        "approve": "approved",
        "prepare": "prepared",
        "publish": "published",
        "fail": "failed",
        "reject": "rejected",
        "archive": "archived",
    }
    if action not in status_by_action:
        raise AppError("Unsupported publish package action", status_code=400)
    try:
        package = await CommercialOperationService(session).set_publish_package_status(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            publish_package_id=publish_package_id,
            status=status_by_action[action],
            actor_user_id=context.user_id,
            reviewer_notes=request.reviewer_notes,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationPublishPackageResponse.from_model(package)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation publish package decision API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation publish package decision failed", status_code=500) from exc


@router.get(
    "/{operation_id}/publish-packages/{publish_package_id}/client-execution-handoff",
    response_model=CommercialOperationPublishExecutionHandoffResponse,
)
async def get_commercial_operation_publish_execution_handoff(
    operation_id: UUID,
    publish_package_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationPublishExecutionHandoffResponse:
    """Build a guarded customer-machine execution handoff for an approved publish package."""

    try:
        response = await CommercialOperationService(session).get_publish_execution_handoff(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            publish_package_id=publish_package_id,
        )
        return CommercialOperationPublishExecutionHandoffResponse(**response)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation publish execution handoff API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation publish execution handoff failed", status_code=500) from exc


@router.post("/{operation_id}/platform-metric-snapshots", response_model=CommercialOperationPlatformMetricSnapshotResponse, status_code=201)
async def create_commercial_operation_platform_metric_snapshot(
    operation_id: UUID,
    request: CommercialOperationPlatformMetricSnapshotCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationPlatformMetricSnapshotResponse:
    """Create a manual or connector-collected platform metric snapshot."""

    try:
        snapshot = await CommercialOperationService(session).create_platform_metric_snapshot(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            collected_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationPlatformMetricSnapshotResponse.from_model(snapshot)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation metric snapshot create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation metric snapshot create failed", status_code=500) from exc


@router.get("/{operation_id}/platform-metric-snapshots", response_model=CommercialOperationPlatformMetricSnapshotListResponse)
async def list_commercial_operation_platform_metric_snapshots(
    operation_id: UUID,
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationPlatformMetricSnapshotListResponse:
    """List platform metric snapshots."""

    try:
        snapshots = await CommercialOperationService(session).list_platform_metric_snapshots(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            limit=limit,
        )
        return CommercialOperationPlatformMetricSnapshotListResponse(
            operation_id=operation_id,
            items=[CommercialOperationPlatformMetricSnapshotResponse.from_model(snapshot) for snapshot in snapshots],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation metric snapshot list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation metric snapshot list failed", status_code=500) from exc


@router.post(
    "/{operation_id}/platform-metric-snapshots/{snapshot_id}/{action}",
    response_model=CommercialOperationPlatformMetricSnapshotResponse,
)
async def decide_commercial_operation_platform_metric_snapshot(
    operation_id: UUID,
    snapshot_id: UUID,
    action: str,
    request: CommercialOperationProjectDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationPlatformMetricSnapshotResponse:
    """Ready, approve, reject, or archive a platform metric snapshot."""

    status_by_action = {"ready": "ready_for_review", "approve": "approved", "reject": "rejected", "archive": "archived"}
    if action not in status_by_action:
        raise AppError("Unsupported platform metric snapshot action", status_code=400)
    try:
        snapshot = await CommercialOperationService(session).set_platform_metric_snapshot_status(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            snapshot_id=snapshot_id,
            status=status_by_action[action],
            actor_user_id=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationPlatformMetricSnapshotResponse.from_model(snapshot)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation metric snapshot decision API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation metric snapshot decision failed", status_code=500) from exc


@router.get("/{operation_id}/metric-analysis-schedule", response_model=CommercialOperationMetricAnalysisScheduleResponse)
async def get_commercial_operation_metric_analysis_schedule(
    operation_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMetricAnalysisScheduleResponse:
    """Read the project-level configurable daily metric analysis schedule."""

    try:
        response = await CommercialOperationService(session).get_metric_analysis_schedule(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
        )
        return CommercialOperationMetricAnalysisScheduleResponse(**response)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation metric analysis schedule read API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation metric analysis schedule read failed", status_code=500) from exc


@router.post("/{operation_id}/metric-analysis-schedule", response_model=CommercialOperationMetricAnalysisScheduleResponse)
async def configure_commercial_operation_metric_analysis_schedule(
    operation_id: UUID,
    request: CommercialOperationMetricAnalysisScheduleRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMetricAnalysisScheduleResponse:
    """Configure the project-level daily metric analysis time and due-state contract."""

    try:
        response = await CommercialOperationService(session).configure_metric_analysis_schedule(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            actor_user_id=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationMetricAnalysisScheduleResponse(**response)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation metric analysis schedule configure API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation metric analysis schedule configure failed", status_code=500) from exc


@router.post("/{operation_id}/metric-analysis-schedule/run", response_model=CommercialOperationMetricAnalysisRunResponse)
async def run_commercial_operation_metric_analysis_schedule(
    operation_id: UUID,
    request: CommercialOperationMetricAnalysisRunRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMetricAnalysisRunResponse:
    """Run or force-run the configured daily metric analysis contract for one project."""

    try:
        response = await CommercialOperationService(session).run_metric_analysis_schedule(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            actor_user_id=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationMetricAnalysisRunResponse(**response)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation metric analysis run API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation metric analysis run failed", status_code=500) from exc


@router.get(
    "/{operation_id}/metric-analysis-schedule/pullback-handoff",
    response_model=CommercialOperationMetricPullbackHandoffResponse,
)
async def get_commercial_operation_metric_pullback_handoff(
    operation_id: UUID,
    force: bool = Query(default=False),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMetricPullbackHandoffResponse:
    """Build a customer-machine metric pullback handoff for the configured daily analysis window."""

    try:
        response = await CommercialOperationService(session).get_metric_pullback_handoff(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            force=force,
        )
        return CommercialOperationMetricPullbackHandoffResponse(**response)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation metric pullback handoff API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation metric pullback handoff failed", status_code=500) from exc


@router.get(
    "/{operation_id}/metric-analysis-schedule/pullback-handoff/adapter-profile",
    response_model=CommercialOperationMetricPullbackAdapterProfileResponse,
)
async def get_commercial_operation_metric_pullback_adapter_profile(
    operation_id: UUID,
    platform: str = Query(default="douyin", min_length=1, max_length=64),
    force: bool = Query(default=False),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMetricPullbackAdapterProfileResponse:
    """Build a platform-specific customer-machine metric pullback adapter profile."""

    try:
        response = await CommercialOperationService(session).get_metric_pullback_adapter_profile(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            platform=platform,
            force=force,
        )
        return CommercialOperationMetricPullbackAdapterProfileResponse(**response)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation metric pullback adapter profile API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation metric pullback adapter profile failed", status_code=500) from exc


@router.post(
    "/{operation_id}/metric-analysis-schedule/pullback-handoff/adapter-profile/parse-export",
    response_model=CommercialOperationMetricPullbackExportImportPreviewResponse,
)
async def preview_commercial_operation_metric_pullback_export_import(
    operation_id: UUID,
    request: CommercialOperationMetricPullbackExportImportPreviewRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMetricPullbackExportImportPreviewResponse:
    """Preview a customer-machine metric export before submitting normalized rows to 68M."""

    try:
        response = await CommercialOperationService(session).preview_metric_pullback_export_import(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            **request.model_dump(),
        )
        return CommercialOperationMetricPullbackExportImportPreviewResponse(**response)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation metric pullback export import preview API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation metric pullback export import preview failed", status_code=500) from exc


@router.post(
    "/{operation_id}/metric-analysis-schedule/pullback-handoff/adapter-profile/browser-assist-session",
    response_model=CommercialOperationMetricPullbackBrowserAssistSessionResponse,
)
async def create_commercial_operation_metric_pullback_browser_assist_session(
    operation_id: UUID,
    request: CommercialOperationMetricPullbackBrowserAssistSessionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMetricPullbackBrowserAssistSessionResponse:
    """Create a guarded customer-machine browser assist session plan for metric pullback."""

    try:
        response = await CommercialOperationService(session).create_metric_pullback_browser_assist_session(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            **request.model_dump(),
        )
        return CommercialOperationMetricPullbackBrowserAssistSessionResponse(**response)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation metric pullback browser assist session API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation metric pullback browser assist session failed", status_code=500) from exc


@router.post(
    "/{operation_id}/metric-analysis-schedule/pullback-handoff/submit-result",
    response_model=CommercialOperationMetricPullbackResultResponse,
)
async def submit_commercial_operation_metric_pullback_result(
    operation_id: UUID,
    request: CommercialOperationMetricPullbackResultRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMetricPullbackResultResponse:
    """Submit customer-machine or connector metric pullback evidence into the scheduled analysis runner."""

    try:
        response = await CommercialOperationService(session).submit_metric_pullback_result(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            actor_user_id=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationMetricPullbackResultResponse(**response)
    except ValueError as exc:
        raise AppError(str(exc), status_code=_status_code_from_value_error(exc)) from exc
    except Exception as exc:
        logger.exception("Commercial operation metric pullback result submit API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation metric pullback result submit failed", status_code=500) from exc


@router.get("/{operation_id}/agent-skill-orchestration", response_model=CommercialOperationAgentSkillOrchestrationResponse)
async def get_commercial_operation_agent_skill_orchestration(
    operation_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationAgentSkillOrchestrationResponse:
    """Read the commercial operation Agent/Skill routing view."""

    try:
        payload = await CommercialOperationService(session).get_agent_skill_orchestration(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
        )
        return CommercialOperationAgentSkillOrchestrationResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation Agent/Skill API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation Agent/Skill orchestration failed", status_code=500) from exc


@router.post("/{operation_id}/agent-skill-orchestration/refresh", response_model=CommercialOperationAgentSkillOrchestrationResponse)
async def refresh_commercial_operation_agent_skill_orchestration(
    operation_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationAgentSkillOrchestrationResponse:
    """Refresh the metadata-only Agent/Skill routing view."""

    return await get_commercial_operation_agent_skill_orchestration(
        operation_id=operation_id,
        session=session,
        context=context,
    )


@router.post("/{operation_id}/main-agent/advance-loop", response_model=CommercialOperationMainAgentAdvanceResponse)
async def advance_commercial_operation_main_agent_loop(
    operation_id: UUID,
    request: CommercialOperationMainAgentAdvanceRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMainAgentAdvanceResponse:
    """Advance one safe, reviewable step in the commercial operation loop."""

    try:
        payload = await CommercialOperationService(session).advance_main_agent_loop(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            actor_user_id=context.user_id,
            dry_run=request.dry_run,
            operator_note=request.operator_note,
            metadata=request.metadata,
        )
        return CommercialOperationMainAgentAdvanceResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation main Agent advance API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation main Agent advance failed", status_code=500) from exc


@router.post("/{operation_id}/video-agent-orchestration", response_model=CommercialOperationVideoAgentOrchestrationResponse)
async def orchestrate_commercial_operation_video_agents(
    operation_id: UUID,
    request: CommercialOperationVideoAgentOrchestrationRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationVideoAgentOrchestrationResponse:
    """Route a commercial operation into the RAG-grounded digital-human video flow."""

    try:
        service = CommercialOperationService(session)
        operation = await service.require_operation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
        )
        rag_context = await _video_agent_rag_context(
            operation=operation,
            request=request,
            session=session,
            workspace_id=context.workspace_id,
        )
        request_context = request.model_dump(mode="json")
        orchestrator = CommercialVideoMainAgent()
        payload = orchestrator.plan(
            operation=operation,
            request_context=request_context,
            rag_context=rag_context,
        )
        video_agent = CommercialVideoAgent()
        video_agent_payload = video_agent.plan(
            operation=operation,
            request_context=request_context,
            rag_context=rag_context,
        )
        payload.update(video_agent_payload)
        digital_human_job: dict[str, Any] | None = None
        if payload["route_decision"]["route"] == "digital_human_video" and request.create_digital_human_job:
            settings = get_settings()
            digital_human_service = DigitalHumanService(settings=settings)
            digital_human_request = payload["digital_human_request"]
            planning_context = dict(digital_human_request.get("planning_context") or {})
            planning_context.update(
                {
                    "video_agent_plan": video_agent_payload.get("video_agent_plan"),
                    "workflow_selection": video_agent_payload.get("workflow_selection"),
                    "execution_package_readiness": (
                        video_agent_payload.get("execution_package", {}).get("readiness")
                    ),
                }
            )
            job_response = await digital_human_service.create_video_job(
                session,
                workspace_id=context.workspace_id,
                user_id=context.user_id,
                objective=str(digital_human_request["objective"]),
                script=str(digital_human_request["script"]),
                provider=request.provider,
                avatar_asset_id=request.avatar_asset_id,
                material_asset_ids=request.material_asset_ids,
                reference_asset_ids=request.reference_asset_ids,
                target_channels=list(digital_human_request.get("target_channels") or []),
                voice_profile=dict(digital_human_request.get("voice_profile") or {}),
                aspect_ratio=str(digital_human_request.get("aspect_ratio") or request.aspect_ratio),
                duration_seconds=request.duration_seconds,
                llm_planning_enabled=request.llm_planning_enabled,
                planning_context=planning_context,
                operator_note="Created by commercial video main agent.",
                metadata={
                    **request.metadata,
                    "source": "commercial_video_main_agent",
                    "phase": "67G",
                    "commercial_operation_id": str(operation_id),
                    "rag_context_status": rag_context.get("status"),
                    "rag_result_count": rag_context.get("rag_result_count"),
                },
            )
            if request.prepare_shot_execution_plan:
                job_response = await digital_human_service.prepare_shot_execution_plan(
                    session,
                    workspace_id=context.workspace_id,
                    job_id=job_response.id,
                    template_id="wan-i2v-reference-avatar",
                    resource_profile="production",
                    width=1080,
                    height=1920,
                    fps=24.0,
                    quality_profile="production",
                    operator_note="Prepared by commercial video main agent.",
                    metadata={
                        "source": "commercial_video_main_agent",
                        "phase": "67G",
                        "commercial_operation_id": str(operation_id),
                    },
                )
            digital_human_job = job_response.model_dump(mode="json")
            payload = orchestrator.plan(
                operation=operation,
                request_context=request_context,
                rag_context=rag_context,
                digital_human_job=digital_human_job,
            )
            payload.update(
                video_agent.plan(
                    operation=operation,
                    request_context=request_context,
                    rag_context=rag_context,
                    digital_human_job=digital_human_job,
                )
            )
        return CommercialOperationVideoAgentOrchestrationResponse(**payload)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except AppError:
        raise
    except Exception as exc:
        logger.exception("Commercial video Agent orchestration API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial video Agent orchestration failed", status_code=500) from exc


@router.post(
    "/{operation_id}/digital-human-delivery-link",
    response_model=CommercialOperationDigitalHumanDeliveryLinkResponse,
    status_code=201,
)
async def link_commercial_operation_digital_human_delivery(
    operation_id: UUID,
    request: CommercialOperationDigitalHumanDeliveryLinkRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDigitalHumanDeliveryLinkResponse:
    """Link a generated digital-human video asset into commercial deliverable packaging."""

    try:
        payload = await CommercialOperationService(session).link_digital_human_delivery_asset(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            digital_human_video_job_id=request.digital_human_video_job_id,
            delivery_asset_id=request.delivery_asset_id,
            content_draft_id=request.content_draft_id,
            step_key=request.step_key,
            channel=request.channel,
            title=request.title,
            purpose=request.purpose,
            actor_user_id=context.user_id,
            metadata=request.metadata,
        )
        return CommercialOperationDigitalHumanDeliveryLinkResponse(
            operation_id=payload["operation_id"],
            workspace_id=payload["workspace_id"],
            link_status=payload["link_status"],
            digital_human_video_job_id=payload["digital_human_video_job_id"],
            delivery_asset_id=payload["delivery_asset_id"],
            deliverable_ready=payload["deliverable_ready"],
            asset_request=CommercialOperationAssetRequestResponse.from_model(payload["asset_request"]),
            next_actions=payload["next_actions"],
            boundaries=payload["boundaries"],
        )
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation digital human delivery link API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation digital human delivery link failed", status_code=500) from exc


@router.post("/{operation_id}/approvals", response_model=CommercialOperationApprovalResponse, status_code=201)
async def create_commercial_operation_approval(
    operation_id: UUID,
    request: CommercialOperationApprovalCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationApprovalResponse:
    """Request human approval for one commercial operation plan step."""

    try:
        approval = await CommercialOperationService(session).create_approval(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            requested_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationApprovalResponse.from_model(approval)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception("Commercial operation approval create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation approval create failed", status_code=500) from exc


@router.get("/{operation_id}/approvals", response_model=CommercialOperationApprovalListResponse)
async def list_commercial_operation_approvals(
    operation_id: UUID,
    status: str | None = Query(default=None, description="pending / approved / rejected / cancelled"),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationApprovalListResponse:
    """List approval gates for a commercial operation."""

    try:
        approvals = await CommercialOperationService(session).list_approvals(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            limit=limit,
        )
        return CommercialOperationApprovalListResponse(
            operation_id=operation_id,
            items=[CommercialOperationApprovalResponse.from_model(approval) for approval in approvals],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation approval list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation approval list failed", status_code=500) from exc


@router.post("/{operation_id}/approvals/{approval_id}/approve", response_model=CommercialOperationApprovalResponse)
async def approve_commercial_operation_approval(
    operation_id: UUID,
    approval_id: UUID,
    request: CommercialOperationApprovalDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationApprovalResponse:
    """Approve a pending commercial operation plan-step gate."""

    try:
        approval = await CommercialOperationService(session).approve_approval(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            approval_id=approval_id,
            reviewer_user_id=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationApprovalResponse.from_model(approval)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation approval approve API failed",
            extra={"operation_id": str(operation_id), "approval_id": str(approval_id)},
        )
        raise AppError("Commercial operation approval approve failed", status_code=500) from exc


@router.post("/{operation_id}/approvals/{approval_id}/reject", response_model=CommercialOperationApprovalResponse)
async def reject_commercial_operation_approval(
    operation_id: UUID,
    approval_id: UUID,
    request: CommercialOperationApprovalDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationApprovalResponse:
    """Reject a pending commercial operation plan-step gate."""

    try:
        approval = await CommercialOperationService(session).reject_approval(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            approval_id=approval_id,
            reviewer_user_id=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationApprovalResponse.from_model(approval)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation approval reject API failed",
            extra={"operation_id": str(operation_id), "approval_id": str(approval_id)},
        )
        raise AppError("Commercial operation approval reject failed", status_code=500) from exc


@router.post("/{operation_id}/approvals/{approval_id}/cancel", response_model=CommercialOperationApprovalResponse)
async def cancel_commercial_operation_approval(
    operation_id: UUID,
    approval_id: UUID,
    request: CommercialOperationApprovalDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationApprovalResponse:
    """Cancel a pending or approved commercial operation plan-step gate before execution."""

    try:
        approval = await CommercialOperationService(session).cancel_approval(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            approval_id=approval_id,
            reviewer_user_id=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationApprovalResponse.from_model(approval)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation approval cancel API failed",
            extra={"operation_id": str(operation_id), "approval_id": str(approval_id)},
        )
        raise AppError("Commercial operation approval cancel failed", status_code=500) from exc


@router.post("/{operation_id}/dry-runs", response_model=CommercialOperationDryRunResponse, status_code=201)
async def create_commercial_operation_dry_run(
    operation_id: UUID,
    request: CommercialOperationDryRunCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDryRunResponse:
    """Create a metadata-only dry-run record from an approved operation approval."""

    try:
        dry_run = await CommercialOperationService(session).create_dry_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            requested_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception("Commercial operation dry-run create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation dry-run create failed", status_code=500) from exc


@router.get("/{operation_id}/dry-runs", response_model=CommercialOperationDryRunListResponse)
async def list_commercial_operation_dry_runs(
    operation_id: UUID,
    status: str | None = Query(default=None, description="created / completed / failed / cancelled"),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDryRunListResponse:
    """List metadata-only dry-run records for a commercial operation."""

    try:
        dry_runs = await CommercialOperationService(session).list_dry_runs(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            limit=limit,
        )
        return CommercialOperationDryRunListResponse(
            operation_id=operation_id,
            items=[CommercialOperationDryRunResponse.from_model(dry_run) for dry_run in dry_runs],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation dry-run list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation dry-run list failed", status_code=500) from exc


@router.post("/{operation_id}/dry-runs/{dry_run_id}/complete", response_model=CommercialOperationDryRunResponse)
async def complete_commercial_operation_dry_run(
    operation_id: UUID,
    dry_run_id: UUID,
    request: CommercialOperationDryRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDryRunResponse:
    """Mark a commercial operation dry-run record as completed without external execution."""

    try:
        dry_run = await CommercialOperationService(session).complete_dry_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            dry_run_id=dry_run_id,
            completed_by=context.user_id,
            result_summary=request.result_summary,
        )
        return CommercialOperationDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation dry-run complete API failed",
            extra={"operation_id": str(operation_id), "dry_run_id": str(dry_run_id)},
        )
        raise AppError("Commercial operation dry-run complete failed", status_code=500) from exc


@router.post("/{operation_id}/dry-runs/{dry_run_id}/fail", response_model=CommercialOperationDryRunResponse)
async def fail_commercial_operation_dry_run(
    operation_id: UUID,
    dry_run_id: UUID,
    request: CommercialOperationDryRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDryRunResponse:
    """Mark a commercial operation dry-run record as failed without retrying external actions."""

    try:
        dry_run = await CommercialOperationService(session).fail_dry_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            dry_run_id=dry_run_id,
            completed_by=context.user_id,
            result_summary=request.result_summary,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation dry-run fail API failed",
            extra={"operation_id": str(operation_id), "dry_run_id": str(dry_run_id)},
        )
        raise AppError("Commercial operation dry-run fail failed", status_code=500) from exc


@router.post("/{operation_id}/dry-runs/{dry_run_id}/cancel", response_model=CommercialOperationDryRunResponse)
async def cancel_commercial_operation_dry_run(
    operation_id: UUID,
    dry_run_id: UUID,
    request: CommercialOperationDryRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDryRunResponse:
    """Cancel a created commercial operation dry-run record."""

    try:
        dry_run = await CommercialOperationService(session).cancel_dry_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            dry_run_id=dry_run_id,
            completed_by=context.user_id,
            result_summary=request.result_summary,
        )
        return CommercialOperationDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation dry-run cancel API failed",
            extra={"operation_id": str(operation_id), "dry_run_id": str(dry_run_id)},
        )
        raise AppError("Commercial operation dry-run cancel failed", status_code=500) from exc


@router.post("/{operation_id}/content-drafts", response_model=CommercialOperationContentDraftResponse, status_code=201)
async def create_commercial_operation_content_draft(
    operation_id: UUID,
    request: CommercialOperationContentDraftCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationContentDraftResponse:
    """Create a non-publishing content draft for a commercial operation channel."""

    try:
        draft = await CommercialOperationService(session).create_content_draft(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            created_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationContentDraftResponse.from_model(draft)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception("Commercial operation content draft create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation content draft create failed", status_code=500) from exc


@router.get("/{operation_id}/content-drafts", response_model=CommercialOperationContentDraftListResponse)
async def list_commercial_operation_content_drafts(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / archived"),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationContentDraftListResponse:
    """List non-publishing content drafts for a commercial operation."""

    try:
        drafts = await CommercialOperationService(session).list_content_drafts(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            limit=limit,
        )
        return CommercialOperationContentDraftListResponse(
            operation_id=operation_id,
            items=[CommercialOperationContentDraftResponse.from_model(draft) for draft in drafts],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation content draft list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation content draft list failed", status_code=500) from exc


@router.post(
    "/{operation_id}/content-drafts/generate-rag",
    response_model=CommercialOperationContentDraftResponse,
    status_code=201,
)
async def generate_commercial_operation_content_draft_from_rag(
    operation_id: UUID,
    request: CommercialOperationContentDraftGenerateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationContentDraftResponse:
    """Generate a draft content record from existing RAG search results."""

    try:
        service = CommercialOperationService(session)
        operation = await service.require_operation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
        )
        settings = get_settings()
        search_mode = request.search_mode or settings.default_search_mode
        if search_mode not in {"dense", "keyword", "hybrid"}:
            raise ValueError("search_mode must be dense, keyword, or hybrid")
        dense_top_k = request.dense_top_k or settings.dense_top_k
        keyword_top_k = request.keyword_top_k or settings.keyword_top_k
        final_top_k = request.final_top_k or settings.final_top_k
        query = _rag_operation_query(
            operation_title=operation.title,
            operation_objective=operation.objective,
            target_audience=operation.target_audience,
            channels=operation.channels,
            success_metrics=operation.success_metrics,
            requested_query=request.query,
        )
        pipeline = create_hybrid_search_pipeline(
            settings=settings,
            session=session,
            collection_name=_clean_optional_text(request.knowledge_collection) or operation.knowledge_collection,
        )
        bundle = await pipeline.search(
            query=query,
            search_mode=search_mode,  # type: ignore[arg-type]
            dense_top_k=dense_top_k,
            keyword_top_k=keyword_top_k,
            source_id=_clean_optional_text(request.source_id),
            workspace_id=context.workspace_id,
        )
        reranked = await RerankerClient(settings=settings).rerank(
            query=query,
            chunks=bundle.merged_results,
            top_n=final_top_k,
        )
        retrieved_chunks = [build_retrieved_chunk_from_reranked(result) for result in reranked]
        evidence_items = [_rag_evidence_item(chunk) for chunk in retrieved_chunks]
        collection_name = pipeline.vector_store.collection_name
        source_materials = _rag_source_materials(collection_name=collection_name, evidence_items=evidence_items)
        summary = _clean_optional_text(request.summary) or (
            f"Generated from {len(evidence_items)} existing RAG chunk(s) for query: {query}"
            if evidence_items
            else f"RAG search returned no chunks for query: {query}"
        )
        draft = await service.create_content_draft(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            step_key=request.step_key,
            channel=request.channel,
            content_format=request.content_format,
            title=_clean_optional_text(request.title) or f"RAG content draft: {operation.title}",
            audience_segment=request.audience_segment or operation.target_audience,
            content_body=_rag_content_draft_body(
                operation_title=operation.title,
                operation_objective=operation.objective,
                target_audience=request.audience_segment or operation.target_audience,
                channel=request.channel,
                content_format=request.content_format,
                query=query,
                evidence_items=evidence_items,
                call_to_action=request.call_to_action,
            ),
            summary=summary,
            call_to_action=request.call_to_action,
            source_materials=source_materials,
            asset_requests=request.asset_requests,
            created_by=context.user_id,
            metadata={
                **request.metadata,
                "source": "commercial_operations_rag_content_generation",
                "phase": "61O",
                "generation_mode": "rag_content_draft",
                "query": query,
                "collection_name": collection_name,
                "source_id": _clean_optional_text(request.source_id),
                "search_mode": search_mode,
                "dense_top_k": dense_top_k,
                "keyword_top_k": keyword_top_k,
                "final_top_k": final_top_k,
                "rag_result_count": len(evidence_items),
                "dense_candidate_count": len(bundle.dense_results),
                "keyword_candidate_count": len(bundle.keyword_results),
                "merged_candidate_count": len(bundle.merged_results),
                "forbidden_actions": [
                    "no knowledge ingestion",
                    "no automatic approval",
                    "no publishing",
                    "no account control",
                    "no ComfyUI, OpenClaw, or browser worker execution",
                ],
            },
        )
        return CommercialOperationContentDraftResponse.from_model(draft)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation RAG content draft generate API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation RAG content draft generate failed", status_code=500) from exc


@router.patch("/{operation_id}/content-drafts/{draft_id}", response_model=CommercialOperationContentDraftResponse)
async def update_commercial_operation_content_draft(
    operation_id: UUID,
    draft_id: UUID,
    request: CommercialOperationContentDraftUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationContentDraftResponse:
    """Patch one commercial operation content draft without publishing it."""

    try:
        draft = await CommercialOperationService(session).update_content_draft(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            draft_id=draft_id,
            updated_by=context.user_id,
            patch=request.model_dump(exclude_unset=True),
        )
        return CommercialOperationContentDraftResponse.from_model(draft)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation content draft update API failed",
            extra={"operation_id": str(operation_id), "draft_id": str(draft_id)},
        )
        raise AppError("Commercial operation content draft update failed", status_code=500) from exc


@router.post("/{operation_id}/content-drafts/{draft_id}/ready", response_model=CommercialOperationContentDraftResponse)
async def ready_commercial_operation_content_draft(
    operation_id: UUID,
    draft_id: UUID,
    request: CommercialOperationContentDraftDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationContentDraftResponse:
    """Mark a content draft ready for human review."""

    try:
        draft = await CommercialOperationService(session).mark_content_draft_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            draft_id=draft_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationContentDraftResponse.from_model(draft)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation content draft ready API failed",
            extra={"operation_id": str(operation_id), "draft_id": str(draft_id)},
        )
        raise AppError("Commercial operation content draft ready failed", status_code=500) from exc


@router.post("/{operation_id}/content-drafts/{draft_id}/approve", response_model=CommercialOperationContentDraftResponse)
async def approve_commercial_operation_content_draft(
    operation_id: UUID,
    draft_id: UUID,
    request: CommercialOperationContentDraftDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationContentDraftResponse:
    """Approve a ready content draft without publishing it."""

    try:
        draft = await CommercialOperationService(session).approve_content_draft(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            draft_id=draft_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationContentDraftResponse.from_model(draft)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation content draft approve API failed",
            extra={"operation_id": str(operation_id), "draft_id": str(draft_id)},
        )
        raise AppError("Commercial operation content draft approve failed", status_code=500) from exc


@router.post("/{operation_id}/content-drafts/{draft_id}/reject", response_model=CommercialOperationContentDraftResponse)
async def reject_commercial_operation_content_draft(
    operation_id: UUID,
    draft_id: UUID,
    request: CommercialOperationContentDraftDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationContentDraftResponse:
    """Reject a ready content draft without publishing it."""

    try:
        draft = await CommercialOperationService(session).reject_content_draft(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            draft_id=draft_id,
            rejected_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationContentDraftResponse.from_model(draft)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation content draft reject API failed",
            extra={"operation_id": str(operation_id), "draft_id": str(draft_id)},
        )
        raise AppError("Commercial operation content draft reject failed", status_code=500) from exc


@router.post("/{operation_id}/content-drafts/{draft_id}/archive", response_model=CommercialOperationContentDraftResponse)
async def archive_commercial_operation_content_draft(
    operation_id: UUID,
    draft_id: UUID,
    request: CommercialOperationContentDraftDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationContentDraftResponse:
    """Archive a content draft without deleting the audit trail."""

    try:
        draft = await CommercialOperationService(session).archive_content_draft(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            draft_id=draft_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationContentDraftResponse.from_model(draft)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation content draft archive API failed",
            extra={"operation_id": str(operation_id), "draft_id": str(draft_id)},
        )
        raise AppError("Commercial operation content draft archive failed", status_code=500) from exc


@router.post(
    "/{operation_id}/asset-requests/generate-rag",
    response_model=CommercialOperationAssetRequestResponse,
    status_code=201,
)
async def generate_commercial_operation_asset_request_from_rag(
    operation_id: UUID,
    request: CommercialOperationAssetRequestGenerateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationAssetRequestResponse:
    """Generate a non-executing asset request brief from existing RAG search results."""

    try:
        service = CommercialOperationService(session)
        operation = await service.require_operation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
        )
        content_draft = None
        if request.content_draft_id is not None:
            content_draft = await service.require_content_draft(
                workspace_id=context.workspace_id,
                operation_id=operation_id,
                draft_id=request.content_draft_id,
            )
        settings = get_settings()
        search_mode = request.search_mode or settings.default_search_mode
        if search_mode not in {"dense", "keyword", "hybrid"}:
            raise ValueError("search_mode must be dense, keyword, or hybrid")
        dense_top_k = request.dense_top_k or settings.dense_top_k
        keyword_top_k = request.keyword_top_k or settings.keyword_top_k
        final_top_k = request.final_top_k or settings.final_top_k
        query = _rag_asset_brief_query(
            operation_title=operation.title,
            operation_objective=operation.objective,
            target_audience=operation.target_audience,
            success_metrics=operation.success_metrics,
            channel=request.channel,
            asset_type=request.asset_type,
            content_draft=content_draft,
            requested_query=request.query,
        )
        pipeline = create_hybrid_search_pipeline(
            settings=settings,
            session=session,
            collection_name=_clean_optional_text(request.knowledge_collection) or operation.knowledge_collection,
        )
        bundle = await pipeline.search(
            query=query,
            search_mode=search_mode,  # type: ignore[arg-type]
            dense_top_k=dense_top_k,
            keyword_top_k=keyword_top_k,
            source_id=_clean_optional_text(request.source_id),
            workspace_id=context.workspace_id,
        )
        reranked = await RerankerClient(settings=settings).rerank(
            query=query,
            chunks=bundle.merged_results,
            top_n=final_top_k,
        )
        retrieved_chunks = [build_retrieved_chunk_from_reranked(result) for result in reranked]
        evidence_items = [_rag_evidence_item(chunk) for chunk in retrieved_chunks]
        collection_name = pipeline.vector_store.collection_name
        source_materials = _rag_source_materials(collection_name=collection_name, evidence_items=evidence_items)
        for material in getattr(content_draft, "source_materials", []) or []:
            if isinstance(material, str) and material.strip() and material.strip() not in source_materials:
                source_materials.append(material.strip())
        purpose = _clean_optional_text(request.purpose) or (
            f"Prepare a reviewable {request.asset_type} asset brief for {request.channel} using existing RAG evidence."
        )
        style_constraints = _clean_optional_text(request.style_constraints) or (
            "Use only reviewed source context; avoid real logos, private data, unreadable text, and unsupported claims."
        )
        asset_request = await service.create_asset_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            step_key=request.step_key,
            content_draft_id=request.content_draft_id,
            channel=request.channel,
            asset_type=request.asset_type,
            title=_clean_optional_text(request.title) or f"RAG asset brief: {operation.title}",
            purpose=purpose,
            dimensions=request.dimensions,
            style_constraints=style_constraints,
            generation_prompt=_rag_asset_generation_prompt(
                operation_title=operation.title,
                operation_objective=operation.objective,
                target_audience=operation.target_audience,
                channel=request.channel,
                asset_type=request.asset_type,
                purpose=purpose,
                style_constraints=style_constraints,
                dimensions=request.dimensions,
                query=query,
                evidence_items=evidence_items,
                content_draft=content_draft,
            ),
            negative_prompt=_clean_optional_text(request.negative_prompt)
            or "No real logos, no private data, no unsupported claims, no unreadable text.",
            source_materials=source_materials,
            readiness_checks=_rag_asset_readiness_checks(
                requested_checks=request.readiness_checks,
                evidence_items=evidence_items,
            ),
            requested_by=context.user_id,
            metadata={
                **request.metadata,
                "source": "commercial_operations_rag_asset_generation",
                "phase": "61P",
                "generation_mode": "rag_asset_brief",
                "query": query,
                "collection_name": collection_name,
                "source_id": _clean_optional_text(request.source_id),
                "search_mode": search_mode,
                "dense_top_k": dense_top_k,
                "keyword_top_k": keyword_top_k,
                "final_top_k": final_top_k,
                "rag_result_count": len(evidence_items),
                "dense_candidate_count": len(bundle.dense_results),
                "keyword_candidate_count": len(bundle.keyword_results),
                "merged_candidate_count": len(bundle.merged_results),
                "content_draft_id": str(request.content_draft_id) if request.content_draft_id else None,
                "forbidden_actions": [
                    "no knowledge ingestion",
                    "no automatic approval",
                    "no publishing",
                    "no account control",
                    "no ComfyUI, OpenClaw, or browser worker execution",
                ],
            },
        )
        return CommercialOperationAssetRequestResponse.from_model(asset_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation RAG asset request generate API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation RAG asset request generate failed", status_code=500) from exc


@router.post("/{operation_id}/asset-requests", response_model=CommercialOperationAssetRequestResponse, status_code=201)
async def create_commercial_operation_asset_request(
    operation_id: UUID,
    request: CommercialOperationAssetRequestCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationAssetRequestResponse:
    """Create a non-executing first-class asset request."""

    try:
        asset_request = await CommercialOperationService(session).create_asset_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            requested_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationAssetRequestResponse.from_model(asset_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception("Commercial operation asset request create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation asset request create failed", status_code=500) from exc


@router.get("/{operation_id}/asset-requests", response_model=CommercialOperationAssetRequestListResponse)
async def list_commercial_operation_asset_requests(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / prepared / failed / archived"),
    content_draft_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationAssetRequestListResponse:
    """List non-executing asset requests for a commercial operation."""

    try:
        asset_requests = await CommercialOperationService(session).list_asset_requests(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            content_draft_id=content_draft_id,
            limit=limit,
        )
        return CommercialOperationAssetRequestListResponse(
            operation_id=operation_id,
            items=[CommercialOperationAssetRequestResponse.from_model(asset_request) for asset_request in asset_requests],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation asset request list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation asset request list failed", status_code=500) from exc


@router.patch("/{operation_id}/asset-requests/{asset_request_id}", response_model=CommercialOperationAssetRequestResponse)
async def update_commercial_operation_asset_request(
    operation_id: UUID,
    asset_request_id: UUID,
    request: CommercialOperationAssetRequestUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationAssetRequestResponse:
    """Patch one asset request without starting generation."""

    try:
        asset_request = await CommercialOperationService(session).update_asset_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            asset_request_id=asset_request_id,
            updated_by=context.user_id,
            patch=request.model_dump(exclude_unset=True),
        )
        return CommercialOperationAssetRequestResponse.from_model(asset_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation asset request update API failed",
            extra={"operation_id": str(operation_id), "asset_request_id": str(asset_request_id)},
        )
        raise AppError("Commercial operation asset request update failed", status_code=500) from exc


@router.post("/{operation_id}/asset-requests/{asset_request_id}/ready", response_model=CommercialOperationAssetRequestResponse)
async def ready_commercial_operation_asset_request(
    operation_id: UUID,
    asset_request_id: UUID,
    request: CommercialOperationAssetRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationAssetRequestResponse:
    """Mark an asset request ready for review."""

    try:
        asset_request = await CommercialOperationService(session).mark_asset_request_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            asset_request_id=asset_request_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationAssetRequestResponse.from_model(asset_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation asset request ready API failed",
            extra={"operation_id": str(operation_id), "asset_request_id": str(asset_request_id)},
        )
        raise AppError("Commercial operation asset request ready failed", status_code=500) from exc


@router.post("/{operation_id}/asset-requests/{asset_request_id}/approve", response_model=CommercialOperationAssetRequestResponse)
async def approve_commercial_operation_asset_request(
    operation_id: UUID,
    asset_request_id: UUID,
    request: CommercialOperationAssetRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationAssetRequestResponse:
    """Approve an asset request without generating assets."""

    try:
        asset_request = await CommercialOperationService(session).approve_asset_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            asset_request_id=asset_request_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationAssetRequestResponse.from_model(asset_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation asset request approve API failed",
            extra={"operation_id": str(operation_id), "asset_request_id": str(asset_request_id)},
        )
        raise AppError("Commercial operation asset request approve failed", status_code=500) from exc


@router.post("/{operation_id}/asset-requests/{asset_request_id}/reject", response_model=CommercialOperationAssetRequestResponse)
async def reject_commercial_operation_asset_request(
    operation_id: UUID,
    asset_request_id: UUID,
    request: CommercialOperationAssetRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationAssetRequestResponse:
    """Reject an asset request without generating assets."""

    try:
        asset_request = await CommercialOperationService(session).reject_asset_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            asset_request_id=asset_request_id,
            rejected_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationAssetRequestResponse.from_model(asset_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation asset request reject API failed",
            extra={"operation_id": str(operation_id), "asset_request_id": str(asset_request_id)},
        )
        raise AppError("Commercial operation asset request reject failed", status_code=500) from exc


@router.post("/{operation_id}/asset-requests/{asset_request_id}/prepare", response_model=CommercialOperationAssetRequestResponse)
async def prepare_commercial_operation_asset_request(
    operation_id: UUID,
    asset_request_id: UUID,
    request: CommercialOperationAssetRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationAssetRequestResponse:
    """Mark an approved asset request prepared for future ComfyUI handoff."""

    try:
        asset_request = await CommercialOperationService(session).prepare_asset_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            asset_request_id=asset_request_id,
            prepared_by=context.user_id,
            result_summary=request.result_summary,
        )
        return CommercialOperationAssetRequestResponse.from_model(asset_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation asset request prepare API failed",
            extra={"operation_id": str(operation_id), "asset_request_id": str(asset_request_id)},
        )
        raise AppError("Commercial operation asset request prepare failed", status_code=500) from exc


@router.post("/{operation_id}/asset-requests/{asset_request_id}/fail", response_model=CommercialOperationAssetRequestResponse)
async def fail_commercial_operation_asset_request(
    operation_id: UUID,
    asset_request_id: UUID,
    request: CommercialOperationAssetRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationAssetRequestResponse:
    """Mark an approved asset request failed during preparation."""

    try:
        asset_request = await CommercialOperationService(session).fail_asset_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            asset_request_id=asset_request_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationAssetRequestResponse.from_model(asset_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation asset request fail API failed",
            extra={"operation_id": str(operation_id), "asset_request_id": str(asset_request_id)},
        )
        raise AppError("Commercial operation asset request fail failed", status_code=500) from exc


@router.post("/{operation_id}/asset-requests/{asset_request_id}/archive", response_model=CommercialOperationAssetRequestResponse)
async def archive_commercial_operation_asset_request(
    operation_id: UUID,
    asset_request_id: UUID,
    request: CommercialOperationAssetRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationAssetRequestResponse:
    """Archive an asset request without deleting the audit trail."""

    try:
        asset_request = await CommercialOperationService(session).archive_asset_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            asset_request_id=asset_request_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationAssetRequestResponse.from_model(asset_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation asset request archive API failed",
            extra={"operation_id": str(operation_id), "asset_request_id": str(asset_request_id)},
        )
        raise AppError("Commercial operation asset request archive failed", status_code=500) from exc


@router.post("/{operation_id}/comfyui-handoffs", response_model=CommercialOperationComfyUIHandoffResponse, status_code=201)
async def create_commercial_operation_comfyui_handoff(
    operation_id: UUID,
    request: CommercialOperationComfyUIHandoffCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIHandoffResponse:
    """Create a metadata-only ComfyUI handoff from an approved asset request."""

    try:
        handoff = await CommercialOperationService(session).create_comfyui_handoff(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            requested_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationComfyUIHandoffResponse.from_model(handoff)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception("Commercial operation ComfyUI handoff create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation ComfyUI handoff create failed", status_code=500) from exc


@router.get("/{operation_id}/comfyui-handoffs", response_model=CommercialOperationComfyUIHandoffListResponse)
async def list_commercial_operation_comfyui_handoffs(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / prepared / failed / archived"),
    asset_request_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIHandoffListResponse:
    """List metadata-only ComfyUI handoffs for a commercial operation."""

    try:
        handoffs = await CommercialOperationService(session).list_comfyui_handoffs(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            asset_request_id=asset_request_id,
            limit=limit,
        )
        return CommercialOperationComfyUIHandoffListResponse(
            operation_id=operation_id,
            items=[CommercialOperationComfyUIHandoffResponse.from_model(handoff) for handoff in handoffs],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation ComfyUI handoff list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation ComfyUI handoff list failed", status_code=500) from exc


@router.patch("/{operation_id}/comfyui-handoffs/{handoff_id}", response_model=CommercialOperationComfyUIHandoffResponse)
async def update_commercial_operation_comfyui_handoff(
    operation_id: UUID,
    handoff_id: UUID,
    request: CommercialOperationComfyUIHandoffUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIHandoffResponse:
    """Patch one metadata-only ComfyUI handoff without submitting jobs."""

    try:
        handoff = await CommercialOperationService(session).update_comfyui_handoff(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            handoff_id=handoff_id,
            updated_by=context.user_id,
            patch=request.model_dump(exclude_unset=True),
        )
        return CommercialOperationComfyUIHandoffResponse.from_model(handoff)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI handoff update API failed",
            extra={"operation_id": str(operation_id), "handoff_id": str(handoff_id)},
        )
        raise AppError("Commercial operation ComfyUI handoff update failed", status_code=500) from exc


@router.post("/{operation_id}/comfyui-handoffs/{handoff_id}/ready", response_model=CommercialOperationComfyUIHandoffResponse)
async def ready_commercial_operation_comfyui_handoff(
    operation_id: UUID,
    handoff_id: UUID,
    request: CommercialOperationComfyUIHandoffDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIHandoffResponse:
    """Mark a metadata-only ComfyUI handoff ready for review."""

    try:
        handoff = await CommercialOperationService(session).mark_comfyui_handoff_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            handoff_id=handoff_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIHandoffResponse.from_model(handoff)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI handoff ready API failed",
            extra={"operation_id": str(operation_id), "handoff_id": str(handoff_id)},
        )
        raise AppError("Commercial operation ComfyUI handoff ready failed", status_code=500) from exc


@router.post("/{operation_id}/comfyui-handoffs/{handoff_id}/approve", response_model=CommercialOperationComfyUIHandoffResponse)
async def approve_commercial_operation_comfyui_handoff(
    operation_id: UUID,
    handoff_id: UUID,
    request: CommercialOperationComfyUIHandoffDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIHandoffResponse:
    """Approve a metadata-only ComfyUI handoff without generating assets."""

    try:
        handoff = await CommercialOperationService(session).approve_comfyui_handoff(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            handoff_id=handoff_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIHandoffResponse.from_model(handoff)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI handoff approve API failed",
            extra={"operation_id": str(operation_id), "handoff_id": str(handoff_id)},
        )
        raise AppError("Commercial operation ComfyUI handoff approve failed", status_code=500) from exc


@router.post("/{operation_id}/comfyui-handoffs/{handoff_id}/reject", response_model=CommercialOperationComfyUIHandoffResponse)
async def reject_commercial_operation_comfyui_handoff(
    operation_id: UUID,
    handoff_id: UUID,
    request: CommercialOperationComfyUIHandoffDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIHandoffResponse:
    """Reject a metadata-only ComfyUI handoff without generating assets."""

    try:
        handoff = await CommercialOperationService(session).reject_comfyui_handoff(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            handoff_id=handoff_id,
            rejected_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIHandoffResponse.from_model(handoff)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI handoff reject API failed",
            extra={"operation_id": str(operation_id), "handoff_id": str(handoff_id)},
        )
        raise AppError("Commercial operation ComfyUI handoff reject failed", status_code=500) from exc


@router.post("/{operation_id}/comfyui-handoffs/{handoff_id}/prepare", response_model=CommercialOperationComfyUIHandoffResponse)
async def prepare_commercial_operation_comfyui_handoff(
    operation_id: UUID,
    handoff_id: UUID,
    request: CommercialOperationComfyUIHandoffDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIHandoffResponse:
    """Mark an approved ComfyUI handoff prepared for a future guarded adapter."""

    try:
        handoff = await CommercialOperationService(session).prepare_comfyui_handoff(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            handoff_id=handoff_id,
            prepared_by=context.user_id,
            result_summary=request.result_summary,
        )
        return CommercialOperationComfyUIHandoffResponse.from_model(handoff)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI handoff prepare API failed",
            extra={"operation_id": str(operation_id), "handoff_id": str(handoff_id)},
        )
        raise AppError("Commercial operation ComfyUI handoff prepare failed", status_code=500) from exc


@router.post("/{operation_id}/comfyui-handoffs/{handoff_id}/fail", response_model=CommercialOperationComfyUIHandoffResponse)
async def fail_commercial_operation_comfyui_handoff(
    operation_id: UUID,
    handoff_id: UUID,
    request: CommercialOperationComfyUIHandoffDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIHandoffResponse:
    """Mark an approved ComfyUI handoff failed during preparation."""

    try:
        handoff = await CommercialOperationService(session).fail_comfyui_handoff(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            handoff_id=handoff_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationComfyUIHandoffResponse.from_model(handoff)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI handoff fail API failed",
            extra={"operation_id": str(operation_id), "handoff_id": str(handoff_id)},
        )
        raise AppError("Commercial operation ComfyUI handoff fail failed", status_code=500) from exc


@router.post("/{operation_id}/comfyui-handoffs/{handoff_id}/archive", response_model=CommercialOperationComfyUIHandoffResponse)
async def archive_commercial_operation_comfyui_handoff(
    operation_id: UUID,
    handoff_id: UUID,
    request: CommercialOperationComfyUIHandoffDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIHandoffResponse:
    """Archive a ComfyUI handoff without deleting the audit trail."""

    try:
        handoff = await CommercialOperationService(session).archive_comfyui_handoff(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            handoff_id=handoff_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIHandoffResponse.from_model(handoff)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI handoff archive API failed",
            extra={"operation_id": str(operation_id), "handoff_id": str(handoff_id)},
        )
        raise AppError("Commercial operation ComfyUI handoff archive failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-handoffs/{handoff_id}/preflights",
    response_model=CommercialOperationComfyUIPreflightResponse,
    status_code=201,
)
async def create_commercial_operation_comfyui_preflight(
    operation_id: UUID,
    handoff_id: UUID,
    request: CommercialOperationComfyUIPreflightCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIPreflightResponse:
    """Create a metadata-only ComfyUI adapter readiness preflight for a handoff."""

    try:
        preflight = await CommercialOperationService(session).create_comfyui_preflight(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            handoff_id=handoff_id,
            checked_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationComfyUIPreflightResponse.from_model(preflight)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI preflight create API failed",
            extra={"operation_id": str(operation_id), "handoff_id": str(handoff_id)},
        )
        raise AppError("Commercial operation ComfyUI preflight create failed", status_code=500) from exc


@router.get("/{operation_id}/comfyui-preflights", response_model=CommercialOperationComfyUIPreflightListResponse)
async def list_commercial_operation_comfyui_preflights(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / checked / blocked / failed / archived"),
    handoff_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIPreflightListResponse:
    """List metadata-only ComfyUI preflights for a commercial operation."""

    try:
        preflights = await CommercialOperationService(session).list_comfyui_preflights(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            handoff_id=handoff_id,
            limit=limit,
        )
        return CommercialOperationComfyUIPreflightListResponse(
            operation_id=operation_id,
            items=[CommercialOperationComfyUIPreflightResponse.from_model(preflight) for preflight in preflights],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation ComfyUI preflight list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation ComfyUI preflight list failed", status_code=500) from exc


@router.patch("/{operation_id}/comfyui-preflights/{preflight_id}", response_model=CommercialOperationComfyUIPreflightResponse)
async def update_commercial_operation_comfyui_preflight(
    operation_id: UUID,
    preflight_id: UUID,
    request: CommercialOperationComfyUIPreflightUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIPreflightResponse:
    """Patch a ComfyUI preflight and rerun metadata-only readiness evaluation."""

    try:
        preflight = await CommercialOperationService(session).update_comfyui_preflight(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            preflight_id=preflight_id,
            patch=request.model_dump(exclude_unset=True),
            updated_by=context.user_id,
        )
        return CommercialOperationComfyUIPreflightResponse.from_model(preflight)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI preflight update API failed",
            extra={"operation_id": str(operation_id), "preflight_id": str(preflight_id)},
        )
        raise AppError("Commercial operation ComfyUI preflight update failed", status_code=500) from exc


@router.post("/{operation_id}/comfyui-preflights/{preflight_id}/check", response_model=CommercialOperationComfyUIPreflightResponse)
async def check_commercial_operation_comfyui_preflight(
    operation_id: UUID,
    preflight_id: UUID,
    request: CommercialOperationComfyUIPreflightDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIPreflightResponse:
    """Re-run local ComfyUI preflight evaluation without calling ComfyUI."""

    _ = request
    try:
        preflight = await CommercialOperationService(session).check_comfyui_preflight(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            preflight_id=preflight_id,
            checked_by=context.user_id,
        )
        return CommercialOperationComfyUIPreflightResponse.from_model(preflight)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI preflight check API failed",
            extra={"operation_id": str(operation_id), "preflight_id": str(preflight_id)},
        )
        raise AppError("Commercial operation ComfyUI preflight check failed", status_code=500) from exc


@router.post("/{operation_id}/comfyui-preflights/{preflight_id}/fail", response_model=CommercialOperationComfyUIPreflightResponse)
async def fail_commercial_operation_comfyui_preflight(
    operation_id: UUID,
    preflight_id: UUID,
    request: CommercialOperationComfyUIPreflightDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIPreflightResponse:
    """Mark a ComfyUI preflight failed without external execution."""

    try:
        preflight = await CommercialOperationService(session).fail_comfyui_preflight(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            preflight_id=preflight_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationComfyUIPreflightResponse.from_model(preflight)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI preflight fail API failed",
            extra={"operation_id": str(operation_id), "preflight_id": str(preflight_id)},
        )
        raise AppError("Commercial operation ComfyUI preflight fail failed", status_code=500) from exc


@router.post("/{operation_id}/comfyui-preflights/{preflight_id}/archive", response_model=CommercialOperationComfyUIPreflightResponse)
async def archive_commercial_operation_comfyui_preflight(
    operation_id: UUID,
    preflight_id: UUID,
    request: CommercialOperationComfyUIPreflightDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIPreflightResponse:
    """Archive a ComfyUI preflight without deleting its audit trail."""

    _ = request
    try:
        preflight = await CommercialOperationService(session).archive_comfyui_preflight(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            preflight_id=preflight_id,
            archived_by=context.user_id,
        )
        return CommercialOperationComfyUIPreflightResponse.from_model(preflight)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI preflight archive API failed",
            extra={"operation_id": str(operation_id), "preflight_id": str(preflight_id)},
        )
        raise AppError("Commercial operation ComfyUI preflight archive failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-configs",
    response_model=CommercialOperationComfyUIAdapterConfigResponse,
    status_code=201,
)
async def create_commercial_operation_comfyui_adapter_config(
    operation_id: UUID,
    request: CommercialOperationComfyUIAdapterConfigCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterConfigResponse:
    """Create a metadata-only ComfyUI adapter config for server maintainers."""

    try:
        config = await CommercialOperationService(session).create_comfyui_adapter_config(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            created_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationComfyUIAdapterConfigResponse.from_model(config)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception("Commercial operation ComfyUI adapter config create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation ComfyUI adapter config create failed", status_code=500) from exc


@router.get("/{operation_id}/comfyui-adapter-configs", response_model=CommercialOperationComfyUIAdapterConfigListResponse)
async def list_commercial_operation_comfyui_adapter_configs(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready / blocked / failed / archived"),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterConfigListResponse:
    """List metadata-only ComfyUI adapter configs for a commercial operation."""

    try:
        configs = await CommercialOperationService(session).list_comfyui_adapter_configs(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            limit=limit,
        )
        return CommercialOperationComfyUIAdapterConfigListResponse(
            operation_id=operation_id,
            items=[CommercialOperationComfyUIAdapterConfigResponse.from_model(config) for config in configs],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation ComfyUI adapter config list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation ComfyUI adapter config list failed", status_code=500) from exc


@router.patch(
    "/{operation_id}/comfyui-adapter-configs/{config_id}",
    response_model=CommercialOperationComfyUIAdapterConfigResponse,
)
async def update_commercial_operation_comfyui_adapter_config(
    operation_id: UUID,
    config_id: UUID,
    request: CommercialOperationComfyUIAdapterConfigUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterConfigResponse:
    """Patch a ComfyUI adapter config and rerun metadata-only validation."""

    try:
        config = await CommercialOperationService(session).update_comfyui_adapter_config(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            config_id=config_id,
            patch=request.model_dump(exclude_unset=True),
            updated_by=context.user_id,
        )
        return CommercialOperationComfyUIAdapterConfigResponse.from_model(config)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter config update API failed",
            extra={"operation_id": str(operation_id), "config_id": str(config_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter config update failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-configs/{config_id}/validate",
    response_model=CommercialOperationComfyUIAdapterConfigResponse,
)
async def validate_commercial_operation_comfyui_adapter_config(
    operation_id: UUID,
    config_id: UUID,
    request: CommercialOperationComfyUIAdapterConfigDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterConfigResponse:
    """Re-run local ComfyUI adapter config validation without calling ComfyUI."""

    _ = request
    try:
        config = await CommercialOperationService(session).validate_comfyui_adapter_config(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            config_id=config_id,
            validated_by=context.user_id,
        )
        return CommercialOperationComfyUIAdapterConfigResponse.from_model(config)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter config validate API failed",
            extra={"operation_id": str(operation_id), "config_id": str(config_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter config validate failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-configs/{config_id}/fail",
    response_model=CommercialOperationComfyUIAdapterConfigResponse,
)
async def fail_commercial_operation_comfyui_adapter_config(
    operation_id: UUID,
    config_id: UUID,
    request: CommercialOperationComfyUIAdapterConfigDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterConfigResponse:
    """Mark a ComfyUI adapter config failed without external execution."""

    try:
        config = await CommercialOperationService(session).fail_comfyui_adapter_config(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            config_id=config_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationComfyUIAdapterConfigResponse.from_model(config)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter config fail API failed",
            extra={"operation_id": str(operation_id), "config_id": str(config_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter config fail failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-configs/{config_id}/archive",
    response_model=CommercialOperationComfyUIAdapterConfigResponse,
)
async def archive_commercial_operation_comfyui_adapter_config(
    operation_id: UUID,
    config_id: UUID,
    request: CommercialOperationComfyUIAdapterConfigDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterConfigResponse:
    """Archive a ComfyUI adapter config without deleting its audit trail."""

    _ = request
    try:
        config = await CommercialOperationService(session).archive_comfyui_adapter_config(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            config_id=config_id,
            archived_by=context.user_id,
        )
        return CommercialOperationComfyUIAdapterConfigResponse.from_model(config)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter config archive API failed",
            extra={"operation_id": str(operation_id), "config_id": str(config_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter config archive failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-preflights/{preflight_id}/job-requests",
    response_model=CommercialOperationComfyUIJobRequestResponse,
    status_code=201,
)
async def create_commercial_operation_comfyui_job_request(
    operation_id: UUID,
    preflight_id: UUID,
    request: CommercialOperationComfyUIJobRequestCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIJobRequestResponse:
    """Create a metadata-only ComfyUI job request from a checked preflight."""

    try:
        job_request = await CommercialOperationService(session).create_comfyui_job_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            preflight_id=preflight_id,
            requested_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationComfyUIJobRequestResponse.from_model(job_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI job request create API failed",
            extra={"operation_id": str(operation_id), "preflight_id": str(preflight_id)},
        )
        raise AppError("Commercial operation ComfyUI job request create failed", status_code=500) from exc


@router.get("/{operation_id}/comfyui-job-requests", response_model=CommercialOperationComfyUIJobRequestListResponse)
async def list_commercial_operation_comfyui_job_requests(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / queued / failed / cancelled / archived"),
    preflight_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIJobRequestListResponse:
    """List metadata-only ComfyUI job requests for a commercial operation."""

    try:
        job_requests = await CommercialOperationService(session).list_comfyui_job_requests(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            preflight_id=preflight_id,
            limit=limit,
        )
        return CommercialOperationComfyUIJobRequestListResponse(
            operation_id=operation_id,
            items=[CommercialOperationComfyUIJobRequestResponse.from_model(item) for item in job_requests],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation ComfyUI job request list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation ComfyUI job request list failed", status_code=500) from exc


@router.patch(
    "/{operation_id}/comfyui-job-requests/{job_request_id}",
    response_model=CommercialOperationComfyUIJobRequestResponse,
)
async def update_commercial_operation_comfyui_job_request(
    operation_id: UUID,
    job_request_id: UUID,
    request: CommercialOperationComfyUIJobRequestUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIJobRequestResponse:
    """Patch a metadata-only ComfyUI job request before queue handoff."""

    try:
        job_request = await CommercialOperationService(session).update_comfyui_job_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            job_request_id=job_request_id,
            patch=request.model_dump(exclude_unset=True),
            updated_by=context.user_id,
        )
        return CommercialOperationComfyUIJobRequestResponse.from_model(job_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI job request update API failed",
            extra={"operation_id": str(operation_id), "job_request_id": str(job_request_id)},
        )
        raise AppError("Commercial operation ComfyUI job request update failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-job-requests/{job_request_id}/ready",
    response_model=CommercialOperationComfyUIJobRequestResponse,
)
async def ready_commercial_operation_comfyui_job_request(
    operation_id: UUID,
    job_request_id: UUID,
    request: CommercialOperationComfyUIJobRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIJobRequestResponse:
    """Mark a metadata-only ComfyUI job request ready for review."""

    try:
        job_request = await CommercialOperationService(session).mark_comfyui_job_request_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            job_request_id=job_request_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIJobRequestResponse.from_model(job_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI job request ready API failed",
            extra={"operation_id": str(operation_id), "job_request_id": str(job_request_id)},
        )
        raise AppError("Commercial operation ComfyUI job request ready failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-job-requests/{job_request_id}/approve",
    response_model=CommercialOperationComfyUIJobRequestResponse,
)
async def approve_commercial_operation_comfyui_job_request(
    operation_id: UUID,
    job_request_id: UUID,
    request: CommercialOperationComfyUIJobRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIJobRequestResponse:
    """Approve a metadata-only ComfyUI job request without submitting it."""

    try:
        job_request = await CommercialOperationService(session).approve_comfyui_job_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            job_request_id=job_request_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIJobRequestResponse.from_model(job_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI job request approve API failed",
            extra={"operation_id": str(operation_id), "job_request_id": str(job_request_id)},
        )
        raise AppError("Commercial operation ComfyUI job request approve failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-job-requests/{job_request_id}/reject",
    response_model=CommercialOperationComfyUIJobRequestResponse,
)
async def reject_commercial_operation_comfyui_job_request(
    operation_id: UUID,
    job_request_id: UUID,
    request: CommercialOperationComfyUIJobRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIJobRequestResponse:
    """Reject a metadata-only ComfyUI job request without submitting it."""

    try:
        job_request = await CommercialOperationService(session).reject_comfyui_job_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            job_request_id=job_request_id,
            rejected_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIJobRequestResponse.from_model(job_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI job request reject API failed",
            extra={"operation_id": str(operation_id), "job_request_id": str(job_request_id)},
        )
        raise AppError("Commercial operation ComfyUI job request reject failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-job-requests/{job_request_id}/queue",
    response_model=CommercialOperationComfyUIJobRequestResponse,
)
async def queue_commercial_operation_comfyui_job_request(
    operation_id: UUID,
    job_request_id: UUID,
    request: CommercialOperationComfyUIJobRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIJobRequestResponse:
    """Mark a ComfyUI job request queued as metadata only; no ComfyUI call occurs."""

    try:
        job_request = await CommercialOperationService(session).queue_comfyui_job_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            job_request_id=job_request_id,
            queued_by=context.user_id,
            result_summary=request.result_summary,
        )
        return CommercialOperationComfyUIJobRequestResponse.from_model(job_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI job request queue API failed",
            extra={"operation_id": str(operation_id), "job_request_id": str(job_request_id)},
        )
        raise AppError("Commercial operation ComfyUI job request queue failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-job-requests/{job_request_id}/fail",
    response_model=CommercialOperationComfyUIJobRequestResponse,
)
async def fail_commercial_operation_comfyui_job_request(
    operation_id: UUID,
    job_request_id: UUID,
    request: CommercialOperationComfyUIJobRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIJobRequestResponse:
    """Mark a ComfyUI job request failed without external execution."""

    try:
        job_request = await CommercialOperationService(session).fail_comfyui_job_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            job_request_id=job_request_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationComfyUIJobRequestResponse.from_model(job_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI job request fail API failed",
            extra={"operation_id": str(operation_id), "job_request_id": str(job_request_id)},
        )
        raise AppError("Commercial operation ComfyUI job request fail failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-job-requests/{job_request_id}/cancel",
    response_model=CommercialOperationComfyUIJobRequestResponse,
)
async def cancel_commercial_operation_comfyui_job_request(
    operation_id: UUID,
    job_request_id: UUID,
    request: CommercialOperationComfyUIJobRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIJobRequestResponse:
    """Cancel a metadata-only ComfyUI job request."""

    try:
        job_request = await CommercialOperationService(session).cancel_comfyui_job_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            job_request_id=job_request_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIJobRequestResponse.from_model(job_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI job request cancel API failed",
            extra={"operation_id": str(operation_id), "job_request_id": str(job_request_id)},
        )
        raise AppError("Commercial operation ComfyUI job request cancel failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-job-requests/{job_request_id}/archive",
    response_model=CommercialOperationComfyUIJobRequestResponse,
)
async def archive_commercial_operation_comfyui_job_request(
    operation_id: UUID,
    job_request_id: UUID,
    request: CommercialOperationComfyUIJobRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIJobRequestResponse:
    """Archive a ComfyUI job request without deleting its audit trail."""

    try:
        job_request = await CommercialOperationService(session).archive_comfyui_job_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            job_request_id=job_request_id,
            archived_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIJobRequestResponse.from_model(job_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI job request archive API failed",
            extra={"operation_id": str(operation_id), "job_request_id": str(job_request_id)},
        )
        raise AppError("Commercial operation ComfyUI job request archive failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-job-requests/{job_request_id}/execution-plans",
    response_model=CommercialOperationComfyUIExecutionPlanResponse,
    status_code=201,
)
async def create_commercial_operation_comfyui_execution_plan(
    operation_id: UUID,
    job_request_id: UUID,
    request: CommercialOperationComfyUIExecutionPlanCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIExecutionPlanResponse:
    """Create a metadata-only ComfyUI execution plan from an approved job request."""

    try:
        plan = await CommercialOperationService(session).create_comfyui_execution_plan(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            job_request_id=job_request_id,
            planned_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationComfyUIExecutionPlanResponse.from_model(plan)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI execution plan create API failed",
            extra={"operation_id": str(operation_id), "job_request_id": str(job_request_id)},
        )
        raise AppError("Commercial operation ComfyUI execution plan create failed", status_code=500) from exc


@router.get("/{operation_id}/comfyui-execution-plans", response_model=CommercialOperationComfyUIExecutionPlanListResponse)
async def list_commercial_operation_comfyui_execution_plans(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / simulated / failed / cancelled / archived"),
    job_request_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIExecutionPlanListResponse:
    """List metadata-only ComfyUI execution plans for a commercial operation."""

    try:
        plans = await CommercialOperationService(session).list_comfyui_execution_plans(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            job_request_id=job_request_id,
            limit=limit,
        )
        return CommercialOperationComfyUIExecutionPlanListResponse(
            operation_id=operation_id,
            items=[CommercialOperationComfyUIExecutionPlanResponse.from_model(item) for item in plans],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation ComfyUI execution plan list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation ComfyUI execution plan list failed", status_code=500) from exc


@router.patch(
    "/{operation_id}/comfyui-execution-plans/{execution_plan_id}",
    response_model=CommercialOperationComfyUIExecutionPlanResponse,
)
async def update_commercial_operation_comfyui_execution_plan(
    operation_id: UUID,
    execution_plan_id: UUID,
    request: CommercialOperationComfyUIExecutionPlanUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIExecutionPlanResponse:
    """Patch a metadata-only ComfyUI execution plan before simulation."""

    try:
        plan = await CommercialOperationService(session).update_comfyui_execution_plan(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_plan_id=execution_plan_id,
            patch=request.model_dump(exclude_unset=True),
            updated_by=context.user_id,
        )
        return CommercialOperationComfyUIExecutionPlanResponse.from_model(plan)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI execution plan update API failed",
            extra={"operation_id": str(operation_id), "execution_plan_id": str(execution_plan_id)},
        )
        raise AppError("Commercial operation ComfyUI execution plan update failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-execution-plans/{execution_plan_id}/ready",
    response_model=CommercialOperationComfyUIExecutionPlanResponse,
)
async def ready_commercial_operation_comfyui_execution_plan(
    operation_id: UUID,
    execution_plan_id: UUID,
    request: CommercialOperationComfyUIExecutionPlanDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIExecutionPlanResponse:
    """Mark a metadata-only ComfyUI execution plan ready for review."""

    try:
        plan = await CommercialOperationService(session).mark_comfyui_execution_plan_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_plan_id=execution_plan_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIExecutionPlanResponse.from_model(plan)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI execution plan ready API failed",
            extra={"operation_id": str(operation_id), "execution_plan_id": str(execution_plan_id)},
        )
        raise AppError("Commercial operation ComfyUI execution plan ready failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-execution-plans/{execution_plan_id}/approve",
    response_model=CommercialOperationComfyUIExecutionPlanResponse,
)
async def approve_commercial_operation_comfyui_execution_plan(
    operation_id: UUID,
    execution_plan_id: UUID,
    request: CommercialOperationComfyUIExecutionPlanDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIExecutionPlanResponse:
    """Approve a metadata-only ComfyUI execution plan without submitting it."""

    try:
        plan = await CommercialOperationService(session).approve_comfyui_execution_plan(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_plan_id=execution_plan_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIExecutionPlanResponse.from_model(plan)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI execution plan approve API failed",
            extra={"operation_id": str(operation_id), "execution_plan_id": str(execution_plan_id)},
        )
        raise AppError("Commercial operation ComfyUI execution plan approve failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-execution-plans/{execution_plan_id}/reject",
    response_model=CommercialOperationComfyUIExecutionPlanResponse,
)
async def reject_commercial_operation_comfyui_execution_plan(
    operation_id: UUID,
    execution_plan_id: UUID,
    request: CommercialOperationComfyUIExecutionPlanDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIExecutionPlanResponse:
    """Reject a metadata-only ComfyUI execution plan without submitting it."""

    try:
        plan = await CommercialOperationService(session).reject_comfyui_execution_plan(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_plan_id=execution_plan_id,
            rejected_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIExecutionPlanResponse.from_model(plan)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI execution plan reject API failed",
            extra={"operation_id": str(operation_id), "execution_plan_id": str(execution_plan_id)},
        )
        raise AppError("Commercial operation ComfyUI execution plan reject failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-execution-plans/{execution_plan_id}/simulate",
    response_model=CommercialOperationComfyUIExecutionPlanResponse,
)
async def simulate_commercial_operation_comfyui_execution_plan(
    operation_id: UUID,
    execution_plan_id: UUID,
    request: CommercialOperationComfyUIExecutionPlanDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIExecutionPlanResponse:
    """Mark a ComfyUI execution plan simulated as metadata only; no ComfyUI call occurs."""

    try:
        plan = await CommercialOperationService(session).simulate_comfyui_execution_plan(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_plan_id=execution_plan_id,
            simulated_by=context.user_id,
            result_summary=request.result_summary,
        )
        return CommercialOperationComfyUIExecutionPlanResponse.from_model(plan)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI execution plan simulate API failed",
            extra={"operation_id": str(operation_id), "execution_plan_id": str(execution_plan_id)},
        )
        raise AppError("Commercial operation ComfyUI execution plan simulate failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-execution-plans/{execution_plan_id}/fail",
    response_model=CommercialOperationComfyUIExecutionPlanResponse,
)
async def fail_commercial_operation_comfyui_execution_plan(
    operation_id: UUID,
    execution_plan_id: UUID,
    request: CommercialOperationComfyUIExecutionPlanDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIExecutionPlanResponse:
    """Mark a ComfyUI execution plan failed without external execution."""

    try:
        plan = await CommercialOperationService(session).fail_comfyui_execution_plan(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_plan_id=execution_plan_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationComfyUIExecutionPlanResponse.from_model(plan)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI execution plan fail API failed",
            extra={"operation_id": str(operation_id), "execution_plan_id": str(execution_plan_id)},
        )
        raise AppError("Commercial operation ComfyUI execution plan fail failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-execution-plans/{execution_plan_id}/cancel",
    response_model=CommercialOperationComfyUIExecutionPlanResponse,
)
async def cancel_commercial_operation_comfyui_execution_plan(
    operation_id: UUID,
    execution_plan_id: UUID,
    request: CommercialOperationComfyUIExecutionPlanDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIExecutionPlanResponse:
    """Cancel a metadata-only ComfyUI execution plan."""

    try:
        plan = await CommercialOperationService(session).cancel_comfyui_execution_plan(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_plan_id=execution_plan_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIExecutionPlanResponse.from_model(plan)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI execution plan cancel API failed",
            extra={"operation_id": str(operation_id), "execution_plan_id": str(execution_plan_id)},
        )
        raise AppError("Commercial operation ComfyUI execution plan cancel failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-execution-plans/{execution_plan_id}/archive",
    response_model=CommercialOperationComfyUIExecutionPlanResponse,
)
async def archive_commercial_operation_comfyui_execution_plan(
    operation_id: UUID,
    execution_plan_id: UUID,
    request: CommercialOperationComfyUIExecutionPlanDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIExecutionPlanResponse:
    """Archive a ComfyUI execution plan without deleting its audit trail."""

    try:
        plan = await CommercialOperationService(session).archive_comfyui_execution_plan(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_plan_id=execution_plan_id,
            archived_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIExecutionPlanResponse.from_model(plan)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI execution plan archive API failed",
            extra={"operation_id": str(operation_id), "execution_plan_id": str(execution_plan_id)},
        )
        raise AppError("Commercial operation ComfyUI execution plan archive failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-execution-plans/{execution_plan_id}/connection-probes",
    response_model=CommercialOperationComfyUIConnectionProbeResponse,
    status_code=201,
)
async def create_commercial_operation_comfyui_connection_probe(
    operation_id: UUID,
    execution_plan_id: UUID,
    request: CommercialOperationComfyUIConnectionProbeCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIConnectionProbeResponse:
    """Create a metadata-only ComfyUI connection probe from an execution plan."""

    try:
        probe = await CommercialOperationService(session).create_comfyui_connection_probe(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_plan_id=execution_plan_id,
            planned_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationComfyUIConnectionProbeResponse.from_model(probe)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI connection probe create API failed",
            extra={"operation_id": str(operation_id), "execution_plan_id": str(execution_plan_id)},
        )
        raise AppError("Commercial operation ComfyUI connection probe create failed", status_code=500) from exc


@router.get("/{operation_id}/comfyui-connection-probes", response_model=CommercialOperationComfyUIConnectionProbeListResponse)
async def list_commercial_operation_comfyui_connection_probes(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / probed / failed / cancelled / archived"),
    execution_plan_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIConnectionProbeListResponse:
    """List metadata-only ComfyUI connection probes for a commercial operation."""

    try:
        probes = await CommercialOperationService(session).list_comfyui_connection_probes(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            execution_plan_id=execution_plan_id,
            limit=limit,
        )
        return CommercialOperationComfyUIConnectionProbeListResponse(
            operation_id=operation_id,
            items=[CommercialOperationComfyUIConnectionProbeResponse.from_model(item) for item in probes],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation ComfyUI connection probe list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation ComfyUI connection probe list failed", status_code=500) from exc


@router.patch(
    "/{operation_id}/comfyui-connection-probes/{connection_probe_id}",
    response_model=CommercialOperationComfyUIConnectionProbeResponse,
)
async def update_commercial_operation_comfyui_connection_probe(
    operation_id: UUID,
    connection_probe_id: UUID,
    request: CommercialOperationComfyUIConnectionProbeUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIConnectionProbeResponse:
    """Patch a metadata-only ComfyUI connection probe before probe recording."""

    try:
        probe = await CommercialOperationService(session).update_comfyui_connection_probe(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            connection_probe_id=connection_probe_id,
            patch=request.model_dump(exclude_unset=True),
            updated_by=context.user_id,
        )
        return CommercialOperationComfyUIConnectionProbeResponse.from_model(probe)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI connection probe update API failed",
            extra={"operation_id": str(operation_id), "connection_probe_id": str(connection_probe_id)},
        )
        raise AppError("Commercial operation ComfyUI connection probe update failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-connection-probes/{connection_probe_id}/ready",
    response_model=CommercialOperationComfyUIConnectionProbeResponse,
)
async def ready_commercial_operation_comfyui_connection_probe(
    operation_id: UUID,
    connection_probe_id: UUID,
    request: CommercialOperationComfyUIConnectionProbeDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIConnectionProbeResponse:
    """Mark a metadata-only ComfyUI connection probe ready for review."""

    try:
        probe = await CommercialOperationService(session).mark_comfyui_connection_probe_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            connection_probe_id=connection_probe_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIConnectionProbeResponse.from_model(probe)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI connection probe ready API failed",
            extra={"operation_id": str(operation_id), "connection_probe_id": str(connection_probe_id)},
        )
        raise AppError("Commercial operation ComfyUI connection probe ready failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-connection-probes/{connection_probe_id}/approve",
    response_model=CommercialOperationComfyUIConnectionProbeResponse,
)
async def approve_commercial_operation_comfyui_connection_probe(
    operation_id: UUID,
    connection_probe_id: UUID,
    request: CommercialOperationComfyUIConnectionProbeDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIConnectionProbeResponse:
    """Approve a metadata-only ComfyUI connection probe without calling ComfyUI."""

    try:
        probe = await CommercialOperationService(session).approve_comfyui_connection_probe(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            connection_probe_id=connection_probe_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIConnectionProbeResponse.from_model(probe)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI connection probe approve API failed",
            extra={"operation_id": str(operation_id), "connection_probe_id": str(connection_probe_id)},
        )
        raise AppError("Commercial operation ComfyUI connection probe approve failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-connection-probes/{connection_probe_id}/reject",
    response_model=CommercialOperationComfyUIConnectionProbeResponse,
)
async def reject_commercial_operation_comfyui_connection_probe(
    operation_id: UUID,
    connection_probe_id: UUID,
    request: CommercialOperationComfyUIConnectionProbeDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIConnectionProbeResponse:
    """Reject a metadata-only ComfyUI connection probe without calling ComfyUI."""

    try:
        probe = await CommercialOperationService(session).reject_comfyui_connection_probe(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            connection_probe_id=connection_probe_id,
            rejected_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIConnectionProbeResponse.from_model(probe)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI connection probe reject API failed",
            extra={"operation_id": str(operation_id), "connection_probe_id": str(connection_probe_id)},
        )
        raise AppError("Commercial operation ComfyUI connection probe reject failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-connection-probes/{connection_probe_id}/probe",
    response_model=CommercialOperationComfyUIConnectionProbeResponse,
)
async def probe_commercial_operation_comfyui_connection_probe(
    operation_id: UUID,
    connection_probe_id: UUID,
    request: CommercialOperationComfyUIConnectionProbeDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIConnectionProbeResponse:
    """Record a metadata-only ComfyUI connection probe; no HTTP call occurs."""

    try:
        probe = await CommercialOperationService(session).probe_comfyui_connection_probe(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            connection_probe_id=connection_probe_id,
            probed_by=context.user_id,
            result_summary=request.result_summary,
        )
        return CommercialOperationComfyUIConnectionProbeResponse.from_model(probe)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI connection probe record API failed",
            extra={"operation_id": str(operation_id), "connection_probe_id": str(connection_probe_id)},
        )
        raise AppError("Commercial operation ComfyUI connection probe record failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-connection-probes/{connection_probe_id}/fail",
    response_model=CommercialOperationComfyUIConnectionProbeResponse,
)
async def fail_commercial_operation_comfyui_connection_probe(
    operation_id: UUID,
    connection_probe_id: UUID,
    request: CommercialOperationComfyUIConnectionProbeDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIConnectionProbeResponse:
    """Mark a ComfyUI connection probe failed without external execution."""

    try:
        probe = await CommercialOperationService(session).fail_comfyui_connection_probe(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            connection_probe_id=connection_probe_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationComfyUIConnectionProbeResponse.from_model(probe)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI connection probe fail API failed",
            extra={"operation_id": str(operation_id), "connection_probe_id": str(connection_probe_id)},
        )
        raise AppError("Commercial operation ComfyUI connection probe fail failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-connection-probes/{connection_probe_id}/cancel",
    response_model=CommercialOperationComfyUIConnectionProbeResponse,
)
async def cancel_commercial_operation_comfyui_connection_probe(
    operation_id: UUID,
    connection_probe_id: UUID,
    request: CommercialOperationComfyUIConnectionProbeDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIConnectionProbeResponse:
    """Cancel a metadata-only ComfyUI connection probe."""

    try:
        probe = await CommercialOperationService(session).cancel_comfyui_connection_probe(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            connection_probe_id=connection_probe_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIConnectionProbeResponse.from_model(probe)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI connection probe cancel API failed",
            extra={"operation_id": str(operation_id), "connection_probe_id": str(connection_probe_id)},
        )
        raise AppError("Commercial operation ComfyUI connection probe cancel failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-connection-probes/{connection_probe_id}/archive",
    response_model=CommercialOperationComfyUIConnectionProbeResponse,
)
async def archive_commercial_operation_comfyui_connection_probe(
    operation_id: UUID,
    connection_probe_id: UUID,
    request: CommercialOperationComfyUIConnectionProbeDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIConnectionProbeResponse:
    """Archive a ComfyUI connection probe without deleting its audit trail."""

    try:
        probe = await CommercialOperationService(session).archive_comfyui_connection_probe(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            connection_probe_id=connection_probe_id,
            archived_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIConnectionProbeResponse.from_model(probe)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI connection probe archive API failed",
            extra={"operation_id": str(operation_id), "connection_probe_id": str(connection_probe_id)},
        )
        raise AppError("Commercial operation ComfyUI connection probe archive failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-connection-probes/{connection_probe_id}/adapter-dispatches",
    response_model=CommercialOperationComfyUIAdapterDispatchResponse,
    status_code=201,
)
async def create_commercial_operation_comfyui_adapter_dispatch(
    operation_id: UUID,
    connection_probe_id: UUID,
    request: CommercialOperationComfyUIAdapterDispatchCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterDispatchResponse:
    """Create a metadata-only ComfyUI adapter dispatch from a probed connection probe."""

    try:
        dispatch = await CommercialOperationService(session).create_comfyui_adapter_dispatch(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            connection_probe_id=connection_probe_id,
            planned_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationComfyUIAdapterDispatchResponse.from_model(dispatch)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter dispatch create API failed",
            extra={"operation_id": str(operation_id), "connection_probe_id": str(connection_probe_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter dispatch create failed", status_code=500) from exc


@router.get("/{operation_id}/comfyui-adapter-dispatches", response_model=CommercialOperationComfyUIAdapterDispatchListResponse)
async def list_commercial_operation_comfyui_adapter_dispatches(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / dispatched / failed / cancelled / archived"),
    connection_probe_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterDispatchListResponse:
    """List metadata-only ComfyUI adapter dispatches for a commercial operation."""

    try:
        dispatches = await CommercialOperationService(session).list_comfyui_adapter_dispatches(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            connection_probe_id=connection_probe_id,
            limit=limit,
        )
        return CommercialOperationComfyUIAdapterDispatchListResponse(
            operation_id=operation_id,
            items=[CommercialOperationComfyUIAdapterDispatchResponse.from_model(item) for item in dispatches],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation ComfyUI adapter dispatch list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation ComfyUI adapter dispatch list failed", status_code=500) from exc


@router.patch(
    "/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}",
    response_model=CommercialOperationComfyUIAdapterDispatchResponse,
)
async def update_commercial_operation_comfyui_adapter_dispatch(
    operation_id: UUID,
    adapter_dispatch_id: UUID,
    request: CommercialOperationComfyUIAdapterDispatchUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterDispatchResponse:
    """Patch a metadata-only ComfyUI adapter dispatch before dispatch recording."""

    try:
        dispatch = await CommercialOperationService(session).update_comfyui_adapter_dispatch(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            adapter_dispatch_id=adapter_dispatch_id,
            patch=request.model_dump(exclude_unset=True),
            updated_by=context.user_id,
        )
        return CommercialOperationComfyUIAdapterDispatchResponse.from_model(dispatch)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter dispatch update API failed",
            extra={"operation_id": str(operation_id), "adapter_dispatch_id": str(adapter_dispatch_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter dispatch update failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/ready",
    response_model=CommercialOperationComfyUIAdapterDispatchResponse,
)
async def ready_commercial_operation_comfyui_adapter_dispatch(
    operation_id: UUID,
    adapter_dispatch_id: UUID,
    request: CommercialOperationComfyUIAdapterDispatchDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterDispatchResponse:
    """Mark a metadata-only ComfyUI adapter dispatch ready for review."""

    try:
        dispatch = await CommercialOperationService(session).mark_comfyui_adapter_dispatch_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            adapter_dispatch_id=adapter_dispatch_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIAdapterDispatchResponse.from_model(dispatch)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter dispatch ready API failed",
            extra={"operation_id": str(operation_id), "adapter_dispatch_id": str(adapter_dispatch_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter dispatch ready failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/approve",
    response_model=CommercialOperationComfyUIAdapterDispatchResponse,
)
async def approve_commercial_operation_comfyui_adapter_dispatch(
    operation_id: UUID,
    adapter_dispatch_id: UUID,
    request: CommercialOperationComfyUIAdapterDispatchDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterDispatchResponse:
    """Approve a metadata-only ComfyUI adapter dispatch without calling ComfyUI."""

    try:
        dispatch = await CommercialOperationService(session).approve_comfyui_adapter_dispatch(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            adapter_dispatch_id=adapter_dispatch_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIAdapterDispatchResponse.from_model(dispatch)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter dispatch approve API failed",
            extra={"operation_id": str(operation_id), "adapter_dispatch_id": str(adapter_dispatch_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter dispatch approve failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/reject",
    response_model=CommercialOperationComfyUIAdapterDispatchResponse,
)
async def reject_commercial_operation_comfyui_adapter_dispatch(
    operation_id: UUID,
    adapter_dispatch_id: UUID,
    request: CommercialOperationComfyUIAdapterDispatchDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterDispatchResponse:
    """Reject a metadata-only ComfyUI adapter dispatch without calling ComfyUI."""

    try:
        dispatch = await CommercialOperationService(session).reject_comfyui_adapter_dispatch(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            adapter_dispatch_id=adapter_dispatch_id,
            rejected_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIAdapterDispatchResponse.from_model(dispatch)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter dispatch reject API failed",
            extra={"operation_id": str(operation_id), "adapter_dispatch_id": str(adapter_dispatch_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter dispatch reject failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/dispatch",
    response_model=CommercialOperationComfyUIAdapterDispatchResponse,
)
async def dispatch_commercial_operation_comfyui_adapter_dispatch(
    operation_id: UUID,
    adapter_dispatch_id: UUID,
    request: CommercialOperationComfyUIAdapterDispatchDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterDispatchResponse:
    """Record a metadata-only ComfyUI adapter dispatch; no adapter call occurs."""

    try:
        dispatch = await CommercialOperationService(session).dispatch_comfyui_adapter_dispatch(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            adapter_dispatch_id=adapter_dispatch_id,
            dispatched_by=context.user_id,
            result_summary=request.result_summary,
        )
        return CommercialOperationComfyUIAdapterDispatchResponse.from_model(dispatch)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter dispatch record API failed",
            extra={"operation_id": str(operation_id), "adapter_dispatch_id": str(adapter_dispatch_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter dispatch record failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/submit-runtime",
    response_model=CommercialOperationComfyUIAdapterDispatchResponse,
)
async def submit_commercial_operation_comfyui_adapter_dispatch_runtime_job(
    operation_id: UUID,
    adapter_dispatch_id: UUID,
    request: CommercialOperationComfyUIRuntimeSubmitRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterDispatchResponse:
    """Submit an approved commercial ComfyUI adapter dispatch through the guarded real runtime adapter."""

    try:
        dispatch = await CommercialOperationService(session).submit_comfyui_adapter_dispatch_runtime_job(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            adapter_dispatch_id=adapter_dispatch_id,
            submitted_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationComfyUIAdapterDispatchResponse.from_model(dispatch)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime submission API failed",
            extra={"operation_id": str(operation_id), "adapter_dispatch_id": str(adapter_dispatch_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime submission failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/refresh-runtime",
    response_model=CommercialOperationComfyUIAdapterDispatchResponse,
)
async def refresh_commercial_operation_comfyui_adapter_dispatch_runtime_job(
    operation_id: UUID,
    adapter_dispatch_id: UUID,
    request: CommercialOperationComfyUIRuntimeSubmitRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterDispatchResponse:
    """Refresh ComfyUI history and queue status for a submitted commercial runtime job."""

    try:
        dispatch = await CommercialOperationService(session).refresh_comfyui_adapter_dispatch_runtime_job(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            adapter_dispatch_id=adapter_dispatch_id,
            refreshed_by=context.user_id,
            poll_history=request.poll_history,
            metadata=request.metadata,
        )
        return CommercialOperationComfyUIAdapterDispatchResponse.from_model(dispatch)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime refresh API failed",
            extra={"operation_id": str(operation_id), "adapter_dispatch_id": str(adapter_dispatch_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime refresh failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/fail",
    response_model=CommercialOperationComfyUIAdapterDispatchResponse,
)
async def fail_commercial_operation_comfyui_adapter_dispatch(
    operation_id: UUID,
    adapter_dispatch_id: UUID,
    request: CommercialOperationComfyUIAdapterDispatchDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterDispatchResponse:
    """Mark a ComfyUI adapter dispatch failed without external execution."""

    try:
        dispatch = await CommercialOperationService(session).fail_comfyui_adapter_dispatch(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            adapter_dispatch_id=adapter_dispatch_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationComfyUIAdapterDispatchResponse.from_model(dispatch)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter dispatch fail API failed",
            extra={"operation_id": str(operation_id), "adapter_dispatch_id": str(adapter_dispatch_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter dispatch fail failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/cancel",
    response_model=CommercialOperationComfyUIAdapterDispatchResponse,
)
async def cancel_commercial_operation_comfyui_adapter_dispatch(
    operation_id: UUID,
    adapter_dispatch_id: UUID,
    request: CommercialOperationComfyUIAdapterDispatchDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterDispatchResponse:
    """Cancel a metadata-only ComfyUI adapter dispatch."""

    try:
        dispatch = await CommercialOperationService(session).cancel_comfyui_adapter_dispatch(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            adapter_dispatch_id=adapter_dispatch_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIAdapterDispatchResponse.from_model(dispatch)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter dispatch cancel API failed",
            extra={"operation_id": str(operation_id), "adapter_dispatch_id": str(adapter_dispatch_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter dispatch cancel failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/archive",
    response_model=CommercialOperationComfyUIAdapterDispatchResponse,
)
async def archive_commercial_operation_comfyui_adapter_dispatch(
    operation_id: UUID,
    adapter_dispatch_id: UUID,
    request: CommercialOperationComfyUIAdapterDispatchDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterDispatchResponse:
    """Archive a ComfyUI adapter dispatch without deleting its audit trail."""

    try:
        dispatch = await CommercialOperationService(session).archive_comfyui_adapter_dispatch(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            adapter_dispatch_id=adapter_dispatch_id,
            archived_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIAdapterDispatchResponse.from_model(dispatch)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter dispatch archive API failed",
            extra={"operation_id": str(operation_id), "adapter_dispatch_id": str(adapter_dispatch_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter dispatch archive failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/runtime-gates",
    response_model=CommercialOperationComfyUIRuntimeGateResponse,
    status_code=201,
)
async def create_commercial_operation_comfyui_runtime_gate(
    operation_id: UUID,
    adapter_dispatch_id: UUID,
    request: CommercialOperationComfyUIRuntimeGateCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeGateResponse:
    """Create a metadata-only ComfyUI runtime gate from a recorded adapter dispatch."""

    try:
        gate = await CommercialOperationService(session).create_comfyui_runtime_gate(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            adapter_dispatch_id=adapter_dispatch_id,
            planned_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationComfyUIRuntimeGateResponse.from_model(gate)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime gate create API failed",
            extra={"operation_id": str(operation_id), "adapter_dispatch_id": str(adapter_dispatch_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime gate create failed", status_code=500) from exc


@router.get("/{operation_id}/comfyui-runtime-gates", response_model=CommercialOperationComfyUIRuntimeGateListResponse)
async def list_commercial_operation_comfyui_runtime_gates(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / armed / disabled / failed / archived"),
    adapter_dispatch_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeGateListResponse:
    """List metadata-only ComfyUI runtime gates for a commercial operation."""

    try:
        gates = await CommercialOperationService(session).list_comfyui_runtime_gates(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            adapter_dispatch_id=adapter_dispatch_id,
            limit=limit,
        )
        return CommercialOperationComfyUIRuntimeGateListResponse(
            operation_id=operation_id,
            items=[CommercialOperationComfyUIRuntimeGateResponse.from_model(item) for item in gates],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation ComfyUI runtime gate list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation ComfyUI runtime gate list failed", status_code=500) from exc


@router.patch(
    "/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}",
    response_model=CommercialOperationComfyUIRuntimeGateResponse,
)
async def update_commercial_operation_comfyui_runtime_gate(
    operation_id: UUID,
    runtime_gate_id: UUID,
    request: CommercialOperationComfyUIRuntimeGateUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeGateResponse:
    """Patch a metadata-only ComfyUI runtime gate before arming."""

    try:
        gate = await CommercialOperationService(session).update_comfyui_runtime_gate(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_gate_id=runtime_gate_id,
            patch=request.model_dump(exclude_unset=True),
            updated_by=context.user_id,
        )
        return CommercialOperationComfyUIRuntimeGateResponse.from_model(gate)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime gate update API failed",
            extra={"operation_id": str(operation_id), "runtime_gate_id": str(runtime_gate_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime gate update failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/ready",
    response_model=CommercialOperationComfyUIRuntimeGateResponse,
)
async def ready_commercial_operation_comfyui_runtime_gate(
    operation_id: UUID,
    runtime_gate_id: UUID,
    request: CommercialOperationComfyUIRuntimeGateDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeGateResponse:
    """Mark a metadata-only ComfyUI runtime gate ready for review."""

    try:
        gate = await CommercialOperationService(session).mark_comfyui_runtime_gate_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_gate_id=runtime_gate_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIRuntimeGateResponse.from_model(gate)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime gate ready API failed",
            extra={"operation_id": str(operation_id), "runtime_gate_id": str(runtime_gate_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime gate ready failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/approve",
    response_model=CommercialOperationComfyUIRuntimeGateResponse,
)
async def approve_commercial_operation_comfyui_runtime_gate(
    operation_id: UUID,
    runtime_gate_id: UUID,
    request: CommercialOperationComfyUIRuntimeGateDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeGateResponse:
    """Approve a metadata-only ComfyUI runtime gate without enabling runtime calls."""

    try:
        gate = await CommercialOperationService(session).approve_comfyui_runtime_gate(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_gate_id=runtime_gate_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIRuntimeGateResponse.from_model(gate)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime gate approve API failed",
            extra={"operation_id": str(operation_id), "runtime_gate_id": str(runtime_gate_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime gate approve failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/reject",
    response_model=CommercialOperationComfyUIRuntimeGateResponse,
)
async def reject_commercial_operation_comfyui_runtime_gate(
    operation_id: UUID,
    runtime_gate_id: UUID,
    request: CommercialOperationComfyUIRuntimeGateDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeGateResponse:
    """Reject a metadata-only ComfyUI runtime gate."""

    try:
        gate = await CommercialOperationService(session).reject_comfyui_runtime_gate(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_gate_id=runtime_gate_id,
            rejected_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIRuntimeGateResponse.from_model(gate)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime gate reject API failed",
            extra={"operation_id": str(operation_id), "runtime_gate_id": str(runtime_gate_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime gate reject failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/arm",
    response_model=CommercialOperationComfyUIRuntimeGateResponse,
)
async def arm_commercial_operation_comfyui_runtime_gate(
    operation_id: UUID,
    runtime_gate_id: UUID,
    request: CommercialOperationComfyUIRuntimeGateDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeGateResponse:
    """Arm a metadata-only ComfyUI runtime gate; no adapter runtime call occurs."""

    try:
        gate = await CommercialOperationService(session).arm_comfyui_runtime_gate(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_gate_id=runtime_gate_id,
            armed_by=context.user_id,
            result_summary=request.result_summary,
        )
        return CommercialOperationComfyUIRuntimeGateResponse.from_model(gate)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime gate arm API failed",
            extra={"operation_id": str(operation_id), "runtime_gate_id": str(runtime_gate_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime gate arm failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/fail",
    response_model=CommercialOperationComfyUIRuntimeGateResponse,
)
async def fail_commercial_operation_comfyui_runtime_gate(
    operation_id: UUID,
    runtime_gate_id: UUID,
    request: CommercialOperationComfyUIRuntimeGateDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeGateResponse:
    """Mark a ComfyUI runtime gate failed without calling ComfyUI."""

    try:
        gate = await CommercialOperationService(session).fail_comfyui_runtime_gate(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_gate_id=runtime_gate_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationComfyUIRuntimeGateResponse.from_model(gate)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime gate fail API failed",
            extra={"operation_id": str(operation_id), "runtime_gate_id": str(runtime_gate_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime gate fail failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/disable",
    response_model=CommercialOperationComfyUIRuntimeGateResponse,
)
async def disable_commercial_operation_comfyui_runtime_gate(
    operation_id: UUID,
    runtime_gate_id: UUID,
    request: CommercialOperationComfyUIRuntimeGateDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeGateResponse:
    """Disable a metadata-only ComfyUI runtime gate."""

    try:
        gate = await CommercialOperationService(session).disable_comfyui_runtime_gate(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_gate_id=runtime_gate_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIRuntimeGateResponse.from_model(gate)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime gate disable API failed",
            extra={"operation_id": str(operation_id), "runtime_gate_id": str(runtime_gate_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime gate disable failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/archive",
    response_model=CommercialOperationComfyUIRuntimeGateResponse,
)
async def archive_commercial_operation_comfyui_runtime_gate(
    operation_id: UUID,
    runtime_gate_id: UUID,
    request: CommercialOperationComfyUIRuntimeGateDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeGateResponse:
    """Archive a ComfyUI runtime gate without deleting its audit trail."""

    try:
        gate = await CommercialOperationService(session).archive_comfyui_runtime_gate(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_gate_id=runtime_gate_id,
            archived_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIRuntimeGateResponse.from_model(gate)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime gate archive API failed",
            extra={"operation_id": str(operation_id), "runtime_gate_id": str(runtime_gate_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime gate archive failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/runtime-dry-runs",
    response_model=CommercialOperationComfyUIRuntimeDryRunResponse,
    status_code=201,
)
async def create_commercial_operation_comfyui_runtime_dry_run(
    operation_id: UUID,
    runtime_gate_id: UUID,
    request: CommercialOperationComfyUIRuntimeDryRunCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeDryRunResponse:
    """Create a metadata-only ComfyUI runtime dry-run from an armed runtime gate."""

    try:
        dry_run = await CommercialOperationService(session).create_comfyui_runtime_dry_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_gate_id=runtime_gate_id,
            planned_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationComfyUIRuntimeDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime dry-run create API failed",
            extra={"operation_id": str(operation_id), "runtime_gate_id": str(runtime_gate_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime dry-run create failed", status_code=500) from exc


@router.get("/{operation_id}/comfyui-runtime-dry-runs", response_model=CommercialOperationComfyUIRuntimeDryRunListResponse)
async def list_commercial_operation_comfyui_runtime_dry_runs(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / validated / failed / cancelled / archived"),
    runtime_gate_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeDryRunListResponse:
    """List metadata-only ComfyUI runtime dry-runs for a commercial operation."""

    try:
        dry_runs = await CommercialOperationService(session).list_comfyui_runtime_dry_runs(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            runtime_gate_id=runtime_gate_id,
            limit=limit,
        )
        return CommercialOperationComfyUIRuntimeDryRunListResponse(
            operation_id=operation_id,
            items=[CommercialOperationComfyUIRuntimeDryRunResponse.from_model(item) for item in dry_runs],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation ComfyUI runtime dry-run list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation ComfyUI runtime dry-run list failed", status_code=500) from exc


@router.patch(
    "/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}",
    response_model=CommercialOperationComfyUIRuntimeDryRunResponse,
)
async def update_commercial_operation_comfyui_runtime_dry_run(
    operation_id: UUID,
    runtime_dry_run_id: UUID,
    request: CommercialOperationComfyUIRuntimeDryRunUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeDryRunResponse:
    """Patch a metadata-only ComfyUI runtime dry-run before validation."""

    try:
        dry_run = await CommercialOperationService(session).update_comfyui_runtime_dry_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_dry_run_id=runtime_dry_run_id,
            patch=request.model_dump(exclude_unset=True),
            updated_by=context.user_id,
        )
        return CommercialOperationComfyUIRuntimeDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime dry-run update API failed",
            extra={"operation_id": str(operation_id), "runtime_dry_run_id": str(runtime_dry_run_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime dry-run update failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/ready",
    response_model=CommercialOperationComfyUIRuntimeDryRunResponse,
)
async def ready_commercial_operation_comfyui_runtime_dry_run(
    operation_id: UUID,
    runtime_dry_run_id: UUID,
    request: CommercialOperationComfyUIRuntimeDryRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeDryRunResponse:
    """Mark a metadata-only ComfyUI runtime dry-run ready for review."""

    try:
        dry_run = await CommercialOperationService(session).mark_comfyui_runtime_dry_run_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_dry_run_id=runtime_dry_run_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIRuntimeDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime dry-run ready API failed",
            extra={"operation_id": str(operation_id), "runtime_dry_run_id": str(runtime_dry_run_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime dry-run ready failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/approve",
    response_model=CommercialOperationComfyUIRuntimeDryRunResponse,
)
async def approve_commercial_operation_comfyui_runtime_dry_run(
    operation_id: UUID,
    runtime_dry_run_id: UUID,
    request: CommercialOperationComfyUIRuntimeDryRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeDryRunResponse:
    """Approve a metadata-only ComfyUI runtime dry-run without enabling runtime calls."""

    try:
        dry_run = await CommercialOperationService(session).approve_comfyui_runtime_dry_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_dry_run_id=runtime_dry_run_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIRuntimeDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime dry-run approve API failed",
            extra={"operation_id": str(operation_id), "runtime_dry_run_id": str(runtime_dry_run_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime dry-run approve failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/reject",
    response_model=CommercialOperationComfyUIRuntimeDryRunResponse,
)
async def reject_commercial_operation_comfyui_runtime_dry_run(
    operation_id: UUID,
    runtime_dry_run_id: UUID,
    request: CommercialOperationComfyUIRuntimeDryRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeDryRunResponse:
    """Reject a metadata-only ComfyUI runtime dry-run."""

    try:
        dry_run = await CommercialOperationService(session).reject_comfyui_runtime_dry_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_dry_run_id=runtime_dry_run_id,
            rejected_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIRuntimeDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime dry-run reject API failed",
            extra={"operation_id": str(operation_id), "runtime_dry_run_id": str(runtime_dry_run_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime dry-run reject failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/validate",
    response_model=CommercialOperationComfyUIRuntimeDryRunResponse,
)
async def validate_commercial_operation_comfyui_runtime_dry_run(
    operation_id: UUID,
    runtime_dry_run_id: UUID,
    request: CommercialOperationComfyUIRuntimeDryRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeDryRunResponse:
    """Validate a metadata-only ComfyUI runtime dry-run; no adapter runtime call occurs."""

    try:
        dry_run = await CommercialOperationService(session).validate_comfyui_runtime_dry_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_dry_run_id=runtime_dry_run_id,
            validated_by=context.user_id,
            result_summary=request.result_summary,
        )
        return CommercialOperationComfyUIRuntimeDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime dry-run validate API failed",
            extra={"operation_id": str(operation_id), "runtime_dry_run_id": str(runtime_dry_run_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime dry-run validate failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/fail",
    response_model=CommercialOperationComfyUIRuntimeDryRunResponse,
)
async def fail_commercial_operation_comfyui_runtime_dry_run(
    operation_id: UUID,
    runtime_dry_run_id: UUID,
    request: CommercialOperationComfyUIRuntimeDryRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeDryRunResponse:
    """Mark a ComfyUI runtime dry-run failed without calling ComfyUI."""

    try:
        dry_run = await CommercialOperationService(session).fail_comfyui_runtime_dry_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_dry_run_id=runtime_dry_run_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationComfyUIRuntimeDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime dry-run fail API failed",
            extra={"operation_id": str(operation_id), "runtime_dry_run_id": str(runtime_dry_run_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime dry-run fail failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/cancel",
    response_model=CommercialOperationComfyUIRuntimeDryRunResponse,
)
async def cancel_commercial_operation_comfyui_runtime_dry_run(
    operation_id: UUID,
    runtime_dry_run_id: UUID,
    request: CommercialOperationComfyUIRuntimeDryRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeDryRunResponse:
    """Cancel a metadata-only ComfyUI runtime dry-run."""

    try:
        dry_run = await CommercialOperationService(session).cancel_comfyui_runtime_dry_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_dry_run_id=runtime_dry_run_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIRuntimeDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime dry-run cancel API failed",
            extra={"operation_id": str(operation_id), "runtime_dry_run_id": str(runtime_dry_run_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime dry-run cancel failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/archive",
    response_model=CommercialOperationComfyUIRuntimeDryRunResponse,
)
async def archive_commercial_operation_comfyui_runtime_dry_run(
    operation_id: UUID,
    runtime_dry_run_id: UUID,
    request: CommercialOperationComfyUIRuntimeDryRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeDryRunResponse:
    """Archive a ComfyUI runtime dry-run without deleting its audit trail."""

    try:
        dry_run = await CommercialOperationService(session).archive_comfyui_runtime_dry_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_dry_run_id=runtime_dry_run_id,
            archived_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIRuntimeDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime dry-run archive API failed",
            extra={"operation_id": str(operation_id), "runtime_dry_run_id": str(runtime_dry_run_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime dry-run archive failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/runtime-activations",
    response_model=CommercialOperationComfyUIRuntimeActivationResponse,
    status_code=201,
)
async def create_commercial_operation_comfyui_runtime_activation(
    operation_id: UUID,
    runtime_dry_run_id: UUID,
    request: CommercialOperationComfyUIRuntimeActivationCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeActivationResponse:
    """Create a metadata-only ComfyUI runtime activation request from a validated dry-run."""

    try:
        activation = await CommercialOperationService(session).create_comfyui_runtime_activation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_dry_run_id=runtime_dry_run_id,
            planned_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationComfyUIRuntimeActivationResponse.from_model(activation)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime activation create API failed",
            extra={"operation_id": str(operation_id), "runtime_dry_run_id": str(runtime_dry_run_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime activation create failed", status_code=500) from exc


@router.get(
    "/{operation_id}/comfyui-runtime-activations",
    response_model=CommercialOperationComfyUIRuntimeActivationListResponse,
)
async def list_commercial_operation_comfyui_runtime_activations(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / scheduled / failed / cancelled / archived"),
    runtime_dry_run_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeActivationListResponse:
    """List metadata-only ComfyUI runtime activation requests for a commercial operation."""

    try:
        activations = await CommercialOperationService(session).list_comfyui_runtime_activations(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            runtime_dry_run_id=runtime_dry_run_id,
            limit=limit,
        )
        return CommercialOperationComfyUIRuntimeActivationListResponse(
            operation_id=operation_id,
            items=[CommercialOperationComfyUIRuntimeActivationResponse.from_model(item) for item in activations],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation ComfyUI runtime activation list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation ComfyUI runtime activation list failed", status_code=500) from exc


@router.patch(
    "/{operation_id}/comfyui-runtime-activations/{runtime_activation_id}",
    response_model=CommercialOperationComfyUIRuntimeActivationResponse,
)
async def update_commercial_operation_comfyui_runtime_activation(
    operation_id: UUID,
    runtime_activation_id: UUID,
    request: CommercialOperationComfyUIRuntimeActivationUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeActivationResponse:
    """Patch a metadata-only ComfyUI runtime activation request before scheduling."""

    try:
        activation = await CommercialOperationService(session).update_comfyui_runtime_activation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_activation_id=runtime_activation_id,
            patch=request.model_dump(exclude_unset=True),
            updated_by=context.user_id,
        )
        return CommercialOperationComfyUIRuntimeActivationResponse.from_model(activation)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime activation update API failed",
            extra={"operation_id": str(operation_id), "runtime_activation_id": str(runtime_activation_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime activation update failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-activations/{runtime_activation_id}/ready",
    response_model=CommercialOperationComfyUIRuntimeActivationResponse,
)
async def ready_commercial_operation_comfyui_runtime_activation(
    operation_id: UUID,
    runtime_activation_id: UUID,
    request: CommercialOperationComfyUIRuntimeActivationDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeActivationResponse:
    """Mark a metadata-only ComfyUI runtime activation request ready for review."""

    try:
        activation = await CommercialOperationService(session).mark_comfyui_runtime_activation_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_activation_id=runtime_activation_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIRuntimeActivationResponse.from_model(activation)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime activation ready API failed",
            extra={"operation_id": str(operation_id), "runtime_activation_id": str(runtime_activation_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime activation ready failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-activations/{runtime_activation_id}/approve",
    response_model=CommercialOperationComfyUIRuntimeActivationResponse,
)
async def approve_commercial_operation_comfyui_runtime_activation(
    operation_id: UUID,
    runtime_activation_id: UUID,
    request: CommercialOperationComfyUIRuntimeActivationDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeActivationResponse:
    """Approve a metadata-only ComfyUI runtime activation request without enabling runtime calls."""

    try:
        activation = await CommercialOperationService(session).approve_comfyui_runtime_activation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_activation_id=runtime_activation_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIRuntimeActivationResponse.from_model(activation)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime activation approve API failed",
            extra={"operation_id": str(operation_id), "runtime_activation_id": str(runtime_activation_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime activation approve failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-activations/{runtime_activation_id}/reject",
    response_model=CommercialOperationComfyUIRuntimeActivationResponse,
)
async def reject_commercial_operation_comfyui_runtime_activation(
    operation_id: UUID,
    runtime_activation_id: UUID,
    request: CommercialOperationComfyUIRuntimeActivationDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeActivationResponse:
    """Reject a metadata-only ComfyUI runtime activation request."""

    try:
        activation = await CommercialOperationService(session).reject_comfyui_runtime_activation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_activation_id=runtime_activation_id,
            rejected_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIRuntimeActivationResponse.from_model(activation)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime activation reject API failed",
            extra={"operation_id": str(operation_id), "runtime_activation_id": str(runtime_activation_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime activation reject failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-activations/{runtime_activation_id}/schedule",
    response_model=CommercialOperationComfyUIRuntimeActivationResponse,
)
async def schedule_commercial_operation_comfyui_runtime_activation(
    operation_id: UUID,
    runtime_activation_id: UUID,
    request: CommercialOperationComfyUIRuntimeActivationDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeActivationResponse:
    """Schedule a metadata-only ComfyUI runtime activation handoff without enabling the switch."""

    try:
        activation = await CommercialOperationService(session).schedule_comfyui_runtime_activation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_activation_id=runtime_activation_id,
            scheduled_by=context.user_id,
            result_summary=request.result_summary,
        )
        return CommercialOperationComfyUIRuntimeActivationResponse.from_model(activation)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime activation schedule API failed",
            extra={"operation_id": str(operation_id), "runtime_activation_id": str(runtime_activation_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime activation schedule failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-activations/{runtime_activation_id}/fail",
    response_model=CommercialOperationComfyUIRuntimeActivationResponse,
)
async def fail_commercial_operation_comfyui_runtime_activation(
    operation_id: UUID,
    runtime_activation_id: UUID,
    request: CommercialOperationComfyUIRuntimeActivationDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeActivationResponse:
    """Mark a ComfyUI runtime activation request failed without external action."""

    try:
        activation = await CommercialOperationService(session).fail_comfyui_runtime_activation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_activation_id=runtime_activation_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationComfyUIRuntimeActivationResponse.from_model(activation)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime activation fail API failed",
            extra={"operation_id": str(operation_id), "runtime_activation_id": str(runtime_activation_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime activation fail failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-activations/{runtime_activation_id}/cancel",
    response_model=CommercialOperationComfyUIRuntimeActivationResponse,
)
async def cancel_commercial_operation_comfyui_runtime_activation(
    operation_id: UUID,
    runtime_activation_id: UUID,
    request: CommercialOperationComfyUIRuntimeActivationDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeActivationResponse:
    """Cancel a metadata-only ComfyUI runtime activation request."""

    try:
        activation = await CommercialOperationService(session).cancel_comfyui_runtime_activation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_activation_id=runtime_activation_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIRuntimeActivationResponse.from_model(activation)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime activation cancel API failed",
            extra={"operation_id": str(operation_id), "runtime_activation_id": str(runtime_activation_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime activation cancel failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-activations/{runtime_activation_id}/archive",
    response_model=CommercialOperationComfyUIRuntimeActivationResponse,
)
async def archive_commercial_operation_comfyui_runtime_activation(
    operation_id: UUID,
    runtime_activation_id: UUID,
    request: CommercialOperationComfyUIRuntimeActivationDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeActivationResponse:
    """Archive a ComfyUI runtime activation request without deleting its audit trail."""

    try:
        activation = await CommercialOperationService(session).archive_comfyui_runtime_activation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_activation_id=runtime_activation_id,
            archived_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIRuntimeActivationResponse.from_model(activation)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime activation archive API failed",
            extra={"operation_id": str(operation_id), "runtime_activation_id": str(runtime_activation_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime activation archive failed", status_code=500) from exc


@router.post("/{operation_id}/deliverables", response_model=CommercialOperationDeliverableResponse, status_code=201)
async def create_commercial_operation_deliverable(
    operation_id: UUID,
    request: CommercialOperationDeliverableCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDeliverableResponse:
    """Create a reviewable deliverable and Output Library artifact without publishing."""

    try:
        deliverable = await CommercialOperationService(session).create_deliverable(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            created_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationDeliverableResponse.from_model(deliverable)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception("Commercial operation deliverable create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation deliverable create failed", status_code=500) from exc


@router.get("/{operation_id}/deliverables", response_model=CommercialOperationDeliverableListResponse)
async def list_commercial_operation_deliverables(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / packaged / failed / archived"),
    content_draft_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDeliverableListResponse:
    """List commercial deliverables for an operation."""

    try:
        deliverables = await CommercialOperationService(session).list_deliverables(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            content_draft_id=content_draft_id,
            limit=limit,
        )
        return CommercialOperationDeliverableListResponse(
            operation_id=operation_id,
            items=[CommercialOperationDeliverableResponse.from_model(deliverable) for deliverable in deliverables],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation deliverable list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation deliverable list failed", status_code=500) from exc


@router.patch("/{operation_id}/deliverables/{deliverable_id}", response_model=CommercialOperationDeliverableResponse)
async def update_commercial_operation_deliverable(
    operation_id: UUID,
    deliverable_id: UUID,
    request: CommercialOperationDeliverableUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDeliverableResponse:
    """Patch a commercial deliverable and refresh its Output Library artifact."""

    try:
        deliverable = await CommercialOperationService(session).update_deliverable(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable_id,
            updated_by=context.user_id,
            patch=request.model_dump(exclude_unset=True),
        )
        return CommercialOperationDeliverableResponse.from_model(deliverable)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation deliverable update API failed",
            extra={"operation_id": str(operation_id), "deliverable_id": str(deliverable_id)},
        )
        raise AppError("Commercial operation deliverable update failed", status_code=500) from exc


@router.post("/{operation_id}/deliverables/{deliverable_id}/ready", response_model=CommercialOperationDeliverableResponse)
async def ready_commercial_operation_deliverable(
    operation_id: UUID,
    deliverable_id: UUID,
    request: CommercialOperationDeliverableDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDeliverableResponse:
    """Mark a commercial deliverable ready for review."""

    try:
        deliverable = await CommercialOperationService(session).mark_deliverable_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationDeliverableResponse.from_model(deliverable)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation deliverable ready API failed",
            extra={"operation_id": str(operation_id), "deliverable_id": str(deliverable_id)},
        )
        raise AppError("Commercial operation deliverable ready failed", status_code=500) from exc


@router.post("/{operation_id}/deliverables/{deliverable_id}/approve", response_model=CommercialOperationDeliverableResponse)
async def approve_commercial_operation_deliverable(
    operation_id: UUID,
    deliverable_id: UUID,
    request: CommercialOperationDeliverableDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDeliverableResponse:
    """Approve a ready commercial deliverable without publishing it."""

    try:
        deliverable = await CommercialOperationService(session).approve_deliverable(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationDeliverableResponse.from_model(deliverable)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation deliverable approve API failed",
            extra={"operation_id": str(operation_id), "deliverable_id": str(deliverable_id)},
        )
        raise AppError("Commercial operation deliverable approve failed", status_code=500) from exc


@router.post("/{operation_id}/deliverables/{deliverable_id}/reject", response_model=CommercialOperationDeliverableResponse)
async def reject_commercial_operation_deliverable(
    operation_id: UUID,
    deliverable_id: UUID,
    request: CommercialOperationDeliverableDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDeliverableResponse:
    """Reject a ready commercial deliverable without publishing it."""

    try:
        deliverable = await CommercialOperationService(session).reject_deliverable(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable_id,
            rejected_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationDeliverableResponse.from_model(deliverable)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation deliverable reject API failed",
            extra={"operation_id": str(operation_id), "deliverable_id": str(deliverable_id)},
        )
        raise AppError("Commercial operation deliverable reject failed", status_code=500) from exc


@router.post("/{operation_id}/deliverables/{deliverable_id}/package", response_model=CommercialOperationDeliverableResponse)
async def package_commercial_operation_deliverable(
    operation_id: UUID,
    deliverable_id: UUID,
    request: CommercialOperationDeliverableDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDeliverableResponse:
    """Package an approved deliverable for operator handoff without external execution."""

    try:
        deliverable = await CommercialOperationService(session).package_deliverable(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable_id,
            packaged_by=context.user_id,
            result_summary=request.result_summary,
        )
        return CommercialOperationDeliverableResponse.from_model(deliverable)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation deliverable package API failed",
            extra={"operation_id": str(operation_id), "deliverable_id": str(deliverable_id)},
        )
        raise AppError("Commercial operation deliverable package failed", status_code=500) from exc


@router.post("/{operation_id}/deliverables/{deliverable_id}/fail", response_model=CommercialOperationDeliverableResponse)
async def fail_commercial_operation_deliverable(
    operation_id: UUID,
    deliverable_id: UUID,
    request: CommercialOperationDeliverableDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDeliverableResponse:
    """Mark an approved deliverable failed during packaging."""

    try:
        deliverable = await CommercialOperationService(session).fail_deliverable(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationDeliverableResponse.from_model(deliverable)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation deliverable fail API failed",
            extra={"operation_id": str(operation_id), "deliverable_id": str(deliverable_id)},
        )
        raise AppError("Commercial operation deliverable fail failed", status_code=500) from exc


@router.post("/{operation_id}/deliverables/{deliverable_id}/archive", response_model=CommercialOperationDeliverableResponse)
async def archive_commercial_operation_deliverable(
    operation_id: UUID,
    deliverable_id: UUID,
    request: CommercialOperationDeliverableDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDeliverableResponse:
    """Archive a commercial deliverable without deleting its artifact trail."""

    try:
        deliverable = await CommercialOperationService(session).archive_deliverable(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationDeliverableResponse.from_model(deliverable)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation deliverable archive API failed",
            extra={"operation_id": str(operation_id), "deliverable_id": str(deliverable_id)},
        )
        raise AppError("Commercial operation deliverable archive failed", status_code=500) from exc


@router.post(
    "/{operation_id}/evidence-snapshots",
    response_model=CommercialOperationEvidenceSnapshotResponse,
    status_code=201,
)
async def create_commercial_operation_evidence_snapshot(
    operation_id: UUID,
    request: CommercialOperationEvidenceSnapshotCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationEvidenceSnapshotResponse:
    """Create a reviewable evidence snapshot from a packaged deliverable."""

    try:
        snapshot = await CommercialOperationService(session).create_evidence_snapshot(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            created_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationEvidenceSnapshotResponse.from_model(snapshot)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation evidence snapshot create API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation evidence snapshot create failed", status_code=500) from exc


@router.get("/{operation_id}/evidence-snapshots", response_model=CommercialOperationEvidenceSnapshotListResponse)
async def list_commercial_operation_evidence_snapshots(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / archived"),
    deliverable_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationEvidenceSnapshotListResponse:
    """List reviewable evidence snapshots for a commercial operation."""

    try:
        snapshots = await CommercialOperationService(session).list_evidence_snapshots(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            deliverable_id=deliverable_id,
            limit=limit,
        )
        return CommercialOperationEvidenceSnapshotListResponse(
            operation_id=operation_id,
            items=[CommercialOperationEvidenceSnapshotResponse.from_model(item) for item in snapshots],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation evidence snapshot list API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation evidence snapshot list failed", status_code=500) from exc


@router.post(
    "/{operation_id}/evidence-snapshots/generate-rag",
    response_model=CommercialOperationEvidenceSnapshotResponse,
    status_code=201,
)
async def generate_commercial_operation_evidence_snapshot_from_rag(
    operation_id: UUID,
    request: CommercialOperationEvidenceSnapshotGenerateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationEvidenceSnapshotResponse:
    """Generate a draft evidence snapshot from existing RAG search results."""

    try:
        service = CommercialOperationService(session)
        operation = await service.require_operation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
        )
        deliverable = await service.require_deliverable(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            deliverable_id=request.deliverable_id,
        )
        if deliverable.deliverable_status != "packaged":
            raise ValueError("Evidence snapshots require a packaged commercial deliverable")

        settings = get_settings()
        search_mode = request.search_mode or settings.default_search_mode
        if search_mode not in {"dense", "keyword", "hybrid"}:
            raise ValueError("search_mode must be dense, keyword, or hybrid")
        dense_top_k = request.dense_top_k or settings.dense_top_k
        keyword_top_k = request.keyword_top_k or settings.keyword_top_k
        final_top_k = request.final_top_k or settings.final_top_k
        query = _rag_generation_query(
            operation_title=operation.title,
            operation_objective=operation.objective,
            deliverable_title=deliverable.title,
            deliverable_summary=deliverable.summary,
            requested_query=request.query,
        )
        pipeline = create_hybrid_search_pipeline(
            settings=settings,
            session=session,
            collection_name=_clean_optional_text(request.knowledge_collection) or operation.knowledge_collection,
        )
        bundle = await pipeline.search(
            query=query,
            search_mode=search_mode,  # type: ignore[arg-type]
            dense_top_k=dense_top_k,
            keyword_top_k=keyword_top_k,
            source_id=_clean_optional_text(request.source_id),
            workspace_id=context.workspace_id,
        )
        reranked = await RerankerClient(settings=settings).rerank(
            query=query,
            chunks=bundle.merged_results,
            top_n=final_top_k,
        )
        retrieved_chunks = [build_retrieved_chunk_from_reranked(result) for result in reranked]
        evidence_items = [_rag_evidence_item(chunk) for chunk in retrieved_chunks]
        source_document_ids = _unique_document_ids(evidence_items)
        coverage_checks = request.coverage_checks or [
            "RAG search completed against the existing knowledge index",
            "operator must review retrieved chunks before approval",
            "no knowledge upload, publishing, account control, or external runtime was executed",
        ]
        if not evidence_items:
            coverage_checks = [
                *coverage_checks,
                "no retrieved chunks; revise the query or attach manual evidence before approval",
            ]
        evidence_summary = _clean_optional_text(request.evidence_summary) or (
            f"Generated from {len(evidence_items)} existing RAG chunk(s) for query: {query}"
            if evidence_items
            else f"RAG search returned no chunks for query: {query}"
        )
        relevance_notes = _clean_optional_text(request.relevance_notes) or (
            "Review the retrieved chunks and approve only if they support the packaged deliverable."
        )
        snapshot = await service.create_evidence_snapshot(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            deliverable_id=request.deliverable_id,
            evidence_type="rag_snapshot",
            title=_clean_optional_text(request.title) or f"RAG evidence draft: {deliverable.title}",
            knowledge_collection=pipeline.vector_store.collection_name,
            query=query,
            evidence_summary=evidence_summary,
            relevance_notes=relevance_notes,
            source_document_ids=source_document_ids,
            source_links=[
                {
                    "title": "RAG search",
                    "target": "/api/v1/rag/search",
                    "collection_name": pipeline.vector_store.collection_name,
                    "query": query,
                    "search_mode": search_mode,
                }
            ],
            evidence_items=evidence_items,
            coverage_checks=coverage_checks,
            snapshot_payload={
                "generation_mode": "rag_search_snapshot",
                "collection_name": pipeline.vector_store.collection_name,
                "query": query,
                "source_id": _clean_optional_text(request.source_id),
                "search_mode": search_mode,
                "dense_top_k": dense_top_k,
                "keyword_top_k": keyword_top_k,
                "final_top_k": final_top_k,
                "result_count": len(evidence_items),
                "dense_candidate_count": len(bundle.dense_results),
                "keyword_candidate_count": len(bundle.keyword_results),
                "merged_candidate_count": len(bundle.merged_results),
                "forbidden_actions": [
                    "no knowledge ingestion",
                    "no automatic approval",
                    "no publishing",
                    "no account control",
                    "no ComfyUI, OpenClaw, or browser worker execution",
                ],
            },
            created_by=context.user_id,
            metadata={
                **request.metadata,
                "source": "commercial_operations_rag_generation",
                "phase": "61N",
            },
        )
        return CommercialOperationEvidenceSnapshotResponse.from_model(snapshot)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation RAG evidence snapshot generation API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation RAG evidence snapshot generation failed", status_code=500) from exc


@router.patch(
    "/{operation_id}/evidence-snapshots/{snapshot_id}",
    response_model=CommercialOperationEvidenceSnapshotResponse,
)
async def update_commercial_operation_evidence_snapshot(
    operation_id: UUID,
    snapshot_id: UUID,
    request: CommercialOperationEvidenceSnapshotUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationEvidenceSnapshotResponse:
    """Patch a draft or rejected commercial evidence snapshot."""

    try:
        snapshot = await CommercialOperationService(session).update_evidence_snapshot(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            snapshot_id=snapshot_id,
            updated_by=context.user_id,
            patch=request.model_dump(exclude_unset=True),
        )
        return CommercialOperationEvidenceSnapshotResponse.from_model(snapshot)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation evidence snapshot update API failed",
            extra={"operation_id": str(operation_id), "snapshot_id": str(snapshot_id)},
        )
        raise AppError("Commercial operation evidence snapshot update failed", status_code=500) from exc


@router.post(
    "/{operation_id}/evidence-snapshots/{snapshot_id}/ready",
    response_model=CommercialOperationEvidenceSnapshotResponse,
)
async def ready_commercial_operation_evidence_snapshot(
    operation_id: UUID,
    snapshot_id: UUID,
    request: CommercialOperationEvidenceSnapshotDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationEvidenceSnapshotResponse:
    """Mark a commercial evidence snapshot ready for review."""

    try:
        snapshot = await CommercialOperationService(session).mark_evidence_snapshot_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            snapshot_id=snapshot_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationEvidenceSnapshotResponse.from_model(snapshot)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation evidence snapshot ready API failed",
            extra={"operation_id": str(operation_id), "snapshot_id": str(snapshot_id)},
        )
        raise AppError("Commercial operation evidence snapshot ready failed", status_code=500) from exc


@router.post(
    "/{operation_id}/evidence-snapshots/{snapshot_id}/approve",
    response_model=CommercialOperationEvidenceSnapshotResponse,
)
async def approve_commercial_operation_evidence_snapshot(
    operation_id: UUID,
    snapshot_id: UUID,
    request: CommercialOperationEvidenceSnapshotDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationEvidenceSnapshotResponse:
    """Approve a reviewed commercial evidence snapshot."""

    try:
        snapshot = await CommercialOperationService(session).approve_evidence_snapshot(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            snapshot_id=snapshot_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationEvidenceSnapshotResponse.from_model(snapshot)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation evidence snapshot approve API failed",
            extra={"operation_id": str(operation_id), "snapshot_id": str(snapshot_id)},
        )
        raise AppError("Commercial operation evidence snapshot approve failed", status_code=500) from exc


@router.post(
    "/{operation_id}/evidence-snapshots/{snapshot_id}/reject",
    response_model=CommercialOperationEvidenceSnapshotResponse,
)
async def reject_commercial_operation_evidence_snapshot(
    operation_id: UUID,
    snapshot_id: UUID,
    request: CommercialOperationEvidenceSnapshotDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationEvidenceSnapshotResponse:
    """Reject a reviewed commercial evidence snapshot for revision."""

    try:
        snapshot = await CommercialOperationService(session).reject_evidence_snapshot(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            snapshot_id=snapshot_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationEvidenceSnapshotResponse.from_model(snapshot)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation evidence snapshot reject API failed",
            extra={"operation_id": str(operation_id), "snapshot_id": str(snapshot_id)},
        )
        raise AppError("Commercial operation evidence snapshot reject failed", status_code=500) from exc


@router.post(
    "/{operation_id}/evidence-snapshots/{snapshot_id}/archive",
    response_model=CommercialOperationEvidenceSnapshotResponse,
)
async def archive_commercial_operation_evidence_snapshot(
    operation_id: UUID,
    snapshot_id: UUID,
    request: CommercialOperationEvidenceSnapshotDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationEvidenceSnapshotResponse:
    """Archive a commercial evidence snapshot while preserving the audit trail."""

    try:
        snapshot = await CommercialOperationService(session).archive_evidence_snapshot(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            snapshot_id=snapshot_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationEvidenceSnapshotResponse.from_model(snapshot)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation evidence snapshot archive API failed",
            extra={"operation_id": str(operation_id), "snapshot_id": str(snapshot_id)},
        )
        raise AppError("Commercial operation evidence snapshot archive failed", status_code=500) from exc


@router.post("/{operation_id}/execution-requests", response_model=CommercialOperationExecutionRequestResponse, status_code=201)
async def create_commercial_operation_execution_request(
    operation_id: UUID,
    request: CommercialOperationExecutionRequestCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRequestResponse:
    """Create a metadata-only monitored execution request from a packaged deliverable."""

    try:
        execution_request = await CommercialOperationService(session).create_execution_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            requested_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationExecutionRequestResponse.from_model(execution_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution request create API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation execution request create failed", status_code=500) from exc


@router.get("/{operation_id}/execution-requests", response_model=CommercialOperationExecutionRequestListResponse)
async def list_commercial_operation_execution_requests(
    operation_id: UUID,
    status: str | None = Query(
        default=None,
        description="draft / ready_for_review / approved / rejected / prepared / failed / cancelled / archived",
    ),
    deliverable_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRequestListResponse:
    """List metadata-only execution requests for a commercial operation."""

    try:
        requests = await CommercialOperationService(session).list_execution_requests(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            deliverable_id=deliverable_id,
            limit=limit,
        )
        return CommercialOperationExecutionRequestListResponse(
            operation_id=operation_id,
            items=[CommercialOperationExecutionRequestResponse.from_model(item) for item in requests],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution request list API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation execution request list failed", status_code=500) from exc


@router.patch(
    "/{operation_id}/execution-requests/{execution_request_id}",
    response_model=CommercialOperationExecutionRequestResponse,
)
async def update_commercial_operation_execution_request(
    operation_id: UUID,
    execution_request_id: UUID,
    request: CommercialOperationExecutionRequestUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRequestResponse:
    """Patch an execution request before it is prepared or archived."""

    try:
        execution_request = await CommercialOperationService(session).update_execution_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
            updated_by=context.user_id,
            patch=request.model_dump(exclude_unset=True),
        )
        return CommercialOperationExecutionRequestResponse.from_model(execution_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution request update API failed",
            extra={"operation_id": str(operation_id), "execution_request_id": str(execution_request_id)},
        )
        raise AppError("Commercial operation execution request update failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-requests/{execution_request_id}/ready",
    response_model=CommercialOperationExecutionRequestResponse,
)
async def ready_commercial_operation_execution_request(
    operation_id: UUID,
    execution_request_id: UUID,
    request: CommercialOperationExecutionRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRequestResponse:
    """Mark an execution request ready for review."""

    try:
        execution_request = await CommercialOperationService(session).mark_execution_request_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationExecutionRequestResponse.from_model(execution_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution request ready API failed",
            extra={"operation_id": str(operation_id), "execution_request_id": str(execution_request_id)},
        )
        raise AppError("Commercial operation execution request ready failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-requests/{execution_request_id}/approve",
    response_model=CommercialOperationExecutionRequestResponse,
)
async def approve_commercial_operation_execution_request(
    operation_id: UUID,
    execution_request_id: UUID,
    request: CommercialOperationExecutionRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRequestResponse:
    """Approve an execution request without executing it."""

    try:
        execution_request = await CommercialOperationService(session).approve_execution_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationExecutionRequestResponse.from_model(execution_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution request approve API failed",
            extra={"operation_id": str(operation_id), "execution_request_id": str(execution_request_id)},
        )
        raise AppError("Commercial operation execution request approve failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-requests/{execution_request_id}/reject",
    response_model=CommercialOperationExecutionRequestResponse,
)
async def reject_commercial_operation_execution_request(
    operation_id: UUID,
    execution_request_id: UUID,
    request: CommercialOperationExecutionRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRequestResponse:
    """Reject an execution request without executing it."""

    try:
        execution_request = await CommercialOperationService(session).reject_execution_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
            rejected_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationExecutionRequestResponse.from_model(execution_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution request reject API failed",
            extra={"operation_id": str(operation_id), "execution_request_id": str(execution_request_id)},
        )
        raise AppError("Commercial operation execution request reject failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-requests/{execution_request_id}/prepare",
    response_model=CommercialOperationExecutionRequestResponse,
)
async def prepare_commercial_operation_execution_request(
    operation_id: UUID,
    execution_request_id: UUID,
    request: CommercialOperationExecutionRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRequestResponse:
    """Prepare an approved request for future guarded runtime handoff."""

    try:
        execution_request = await CommercialOperationService(session).prepare_execution_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
            prepared_by=context.user_id,
            result_summary=request.result_summary,
        )
        return CommercialOperationExecutionRequestResponse.from_model(execution_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution request prepare API failed",
            extra={"operation_id": str(operation_id), "execution_request_id": str(execution_request_id)},
        )
        raise AppError("Commercial operation execution request prepare failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-requests/{execution_request_id}/fail",
    response_model=CommercialOperationExecutionRequestResponse,
)
async def fail_commercial_operation_execution_request(
    operation_id: UUID,
    execution_request_id: UUID,
    request: CommercialOperationExecutionRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRequestResponse:
    """Mark an approved execution request failed before any external runtime action."""

    try:
        execution_request = await CommercialOperationService(session).fail_execution_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationExecutionRequestResponse.from_model(execution_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution request fail API failed",
            extra={"operation_id": str(operation_id), "execution_request_id": str(execution_request_id)},
        )
        raise AppError("Commercial operation execution request fail failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-requests/{execution_request_id}/cancel",
    response_model=CommercialOperationExecutionRequestResponse,
)
async def cancel_commercial_operation_execution_request(
    operation_id: UUID,
    execution_request_id: UUID,
    request: CommercialOperationExecutionRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRequestResponse:
    """Cancel an execution request before it is prepared."""

    try:
        execution_request = await CommercialOperationService(session).cancel_execution_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationExecutionRequestResponse.from_model(execution_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution request cancel API failed",
            extra={"operation_id": str(operation_id), "execution_request_id": str(execution_request_id)},
        )
        raise AppError("Commercial operation execution request cancel failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-requests/{execution_request_id}/archive",
    response_model=CommercialOperationExecutionRequestResponse,
)
async def archive_commercial_operation_execution_request(
    operation_id: UUID,
    execution_request_id: UUID,
    request: CommercialOperationExecutionRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRequestResponse:
    """Archive an execution request while preserving the audit trail."""

    try:
        execution_request = await CommercialOperationService(session).archive_execution_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationExecutionRequestResponse.from_model(execution_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution request archive API failed",
            extra={"operation_id": str(operation_id), "execution_request_id": str(execution_request_id)},
        )
        raise AppError("Commercial operation execution request archive failed", status_code=500) from exc


@router.post("/{operation_id}/execution-runs", response_model=CommercialOperationExecutionRunResponse, status_code=201)
async def create_commercial_operation_execution_run(
    operation_id: UUID,
    request: CommercialOperationExecutionRunCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRunResponse:
    """Create a metadata-only execution run record from a prepared execution request."""

    try:
        execution_run = await CommercialOperationService(session).create_execution_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            queued_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationExecutionRunResponse.from_model(execution_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution run create API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation execution run create failed", status_code=500) from exc


@router.get("/{operation_id}/execution-runs", response_model=CommercialOperationExecutionRunListResponse)
async def list_commercial_operation_execution_runs(
    operation_id: UUID,
    status: str | None = Query(
        default=None,
        description="queued / running / succeeded / failed / retrying / cancelled / archived",
    ),
    execution_request_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRunListResponse:
    """List metadata-only execution run records for a commercial operation."""

    try:
        execution_runs = await CommercialOperationService(session).list_execution_runs(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            execution_request_id=execution_request_id,
            limit=limit,
        )
        return CommercialOperationExecutionRunListResponse(
            operation_id=operation_id,
            items=[CommercialOperationExecutionRunResponse.from_model(item) for item in execution_runs],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution run list API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation execution run list failed", status_code=500) from exc


@router.patch(
    "/{operation_id}/execution-runs/{execution_run_id}",
    response_model=CommercialOperationExecutionRunResponse,
)
async def update_commercial_operation_execution_run(
    operation_id: UUID,
    execution_run_id: UUID,
    request: CommercialOperationExecutionRunUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRunResponse:
    """Patch a queued or retrying metadata-only execution run record."""

    try:
        execution_run = await CommercialOperationService(session).update_execution_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_run_id=execution_run_id,
            updated_by=context.user_id,
            patch=request.model_dump(exclude_unset=True),
        )
        return CommercialOperationExecutionRunResponse.from_model(execution_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution run update API failed",
            extra={"operation_id": str(operation_id), "execution_run_id": str(execution_run_id)},
        )
        raise AppError("Commercial operation execution run update failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-runs/{execution_run_id}/start",
    response_model=CommercialOperationExecutionRunResponse,
)
async def start_commercial_operation_execution_run(
    operation_id: UUID,
    execution_run_id: UUID,
    request: CommercialOperationExecutionRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRunResponse:
    """Mark a metadata-only execution run as running without calling an external runtime."""

    try:
        execution_run = await CommercialOperationService(session).start_execution_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_run_id=execution_run_id,
            started_by=context.user_id,
            operator_notes=request.operator_notes,
        )
        return CommercialOperationExecutionRunResponse.from_model(execution_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution run start API failed",
            extra={"operation_id": str(operation_id), "execution_run_id": str(execution_run_id)},
        )
        raise AppError("Commercial operation execution run start failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-runs/{execution_run_id}/succeed",
    response_model=CommercialOperationExecutionRunResponse,
)
async def succeed_commercial_operation_execution_run(
    operation_id: UUID,
    execution_run_id: UUID,
    request: CommercialOperationExecutionRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRunResponse:
    """Mark a metadata-only execution run succeeded and record operator results."""

    try:
        execution_run = await CommercialOperationService(session).succeed_execution_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_run_id=execution_run_id,
            completed_by=context.user_id,
            result_summary=request.result_summary,
            result_payload=request.result_payload,
        )
        return CommercialOperationExecutionRunResponse.from_model(execution_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution run succeed API failed",
            extra={"operation_id": str(operation_id), "execution_run_id": str(execution_run_id)},
        )
        raise AppError("Commercial operation execution run succeed failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-runs/{execution_run_id}/fail",
    response_model=CommercialOperationExecutionRunResponse,
)
async def fail_commercial_operation_execution_run(
    operation_id: UUID,
    execution_run_id: UUID,
    request: CommercialOperationExecutionRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRunResponse:
    """Mark a metadata-only execution run failed and record recovery context."""

    try:
        execution_run = await CommercialOperationService(session).fail_execution_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_run_id=execution_run_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
            result_payload=request.result_payload,
        )
        return CommercialOperationExecutionRunResponse.from_model(execution_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution run fail API failed",
            extra={"operation_id": str(operation_id), "execution_run_id": str(execution_run_id)},
        )
        raise AppError("Commercial operation execution run fail failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-runs/{execution_run_id}/retry",
    response_model=CommercialOperationExecutionRunResponse,
)
async def retry_commercial_operation_execution_run(
    operation_id: UUID,
    execution_run_id: UUID,
    request: CommercialOperationExecutionRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRunResponse:
    """Move a failed metadata-only execution run into retrying state."""

    try:
        execution_run = await CommercialOperationService(session).retry_execution_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_run_id=execution_run_id,
            updated_by=context.user_id,
            operator_notes=request.operator_notes,
        )
        return CommercialOperationExecutionRunResponse.from_model(execution_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution run retry API failed",
            extra={"operation_id": str(operation_id), "execution_run_id": str(execution_run_id)},
        )
        raise AppError("Commercial operation execution run retry failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-runs/{execution_run_id}/cancel",
    response_model=CommercialOperationExecutionRunResponse,
)
async def cancel_commercial_operation_execution_run(
    operation_id: UUID,
    execution_run_id: UUID,
    request: CommercialOperationExecutionRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRunResponse:
    """Cancel a queued, running, or retrying metadata-only execution run."""

    try:
        execution_run = await CommercialOperationService(session).cancel_execution_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_run_id=execution_run_id,
            updated_by=context.user_id,
            operator_notes=request.operator_notes,
        )
        return CommercialOperationExecutionRunResponse.from_model(execution_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution run cancel API failed",
            extra={"operation_id": str(operation_id), "execution_run_id": str(execution_run_id)},
        )
        raise AppError("Commercial operation execution run cancel failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-runs/{execution_run_id}/archive",
    response_model=CommercialOperationExecutionRunResponse,
)
async def archive_commercial_operation_execution_run(
    operation_id: UUID,
    execution_run_id: UUID,
    request: CommercialOperationExecutionRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRunResponse:
    """Archive a metadata-only execution run while preserving the audit trail."""

    try:
        execution_run = await CommercialOperationService(session).archive_execution_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_run_id=execution_run_id,
            updated_by=context.user_id,
            operator_notes=request.operator_notes,
        )
        return CommercialOperationExecutionRunResponse.from_model(execution_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution run archive API failed",
            extra={"operation_id": str(operation_id), "execution_run_id": str(execution_run_id)},
        )
        raise AppError("Commercial operation execution run archive failed", status_code=500) from exc


@router.post("/{operation_id}/results", response_model=CommercialOperationResultResponse, status_code=201)
async def create_commercial_operation_result(
    operation_id: UUID,
    request: CommercialOperationResultCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationResultResponse:
    """Create an operator-reviewed commercial result record from a terminal execution run."""

    try:
        result = await CommercialOperationService(session).create_result(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            created_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationResultResponse.from_model(result)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception("Commercial operation result create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation result create failed", status_code=500) from exc


@router.get("/{operation_id}/results", response_model=CommercialOperationResultListResponse)
async def list_commercial_operation_results(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / archived"),
    execution_run_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationResultListResponse:
    """List operator-reviewed commercial result records for a commercial operation."""

    try:
        results = await CommercialOperationService(session).list_results(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            execution_run_id=execution_run_id,
            limit=limit,
        )
        return CommercialOperationResultListResponse(
            operation_id=operation_id,
            items=[CommercialOperationResultResponse.from_model(item) for item in results],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation result list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation result list failed", status_code=500) from exc


@router.patch("/{operation_id}/results/{result_id}", response_model=CommercialOperationResultResponse)
async def update_commercial_operation_result(
    operation_id: UUID,
    result_id: UUID,
    request: CommercialOperationResultUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationResultResponse:
    """Patch a draft or rejected commercial result record."""

    try:
        result = await CommercialOperationService(session).update_result(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            result_id=result_id,
            updated_by=context.user_id,
            patch=request.model_dump(exclude_unset=True),
        )
        return CommercialOperationResultResponse.from_model(result)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation result update API failed",
            extra={"operation_id": str(operation_id), "result_id": str(result_id)},
        )
        raise AppError("Commercial operation result update failed", status_code=500) from exc


@router.post("/{operation_id}/results/{result_id}/ready", response_model=CommercialOperationResultResponse)
async def ready_commercial_operation_result(
    operation_id: UUID,
    result_id: UUID,
    request: CommercialOperationResultDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationResultResponse:
    """Mark a commercial result ready for review."""

    try:
        result = await CommercialOperationService(session).mark_result_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            result_id=result_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationResultResponse.from_model(result)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation result ready API failed",
            extra={"operation_id": str(operation_id), "result_id": str(result_id)},
        )
        raise AppError("Commercial operation result ready failed", status_code=500) from exc


@router.post("/{operation_id}/results/{result_id}/approve", response_model=CommercialOperationResultResponse)
async def approve_commercial_operation_result(
    operation_id: UUID,
    result_id: UUID,
    request: CommercialOperationResultDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationResultResponse:
    """Approve a reviewed commercial result record."""

    try:
        result = await CommercialOperationService(session).approve_result(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            result_id=result_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationResultResponse.from_model(result)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation result approve API failed",
            extra={"operation_id": str(operation_id), "result_id": str(result_id)},
        )
        raise AppError("Commercial operation result approve failed", status_code=500) from exc


@router.post("/{operation_id}/results/{result_id}/reject", response_model=CommercialOperationResultResponse)
async def reject_commercial_operation_result(
    operation_id: UUID,
    result_id: UUID,
    request: CommercialOperationResultDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationResultResponse:
    """Reject a reviewed commercial result record for revision."""

    try:
        result = await CommercialOperationService(session).reject_result(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            result_id=result_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationResultResponse.from_model(result)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation result reject API failed",
            extra={"operation_id": str(operation_id), "result_id": str(result_id)},
        )
        raise AppError("Commercial operation result reject failed", status_code=500) from exc


@router.post("/{operation_id}/results/{result_id}/archive", response_model=CommercialOperationResultResponse)
async def archive_commercial_operation_result(
    operation_id: UUID,
    result_id: UUID,
    request: CommercialOperationResultDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationResultResponse:
    """Archive a commercial result record while preserving the audit trail."""

    try:
        result = await CommercialOperationService(session).archive_result(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            result_id=result_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationResultResponse.from_model(result)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation result archive API failed",
            extra={"operation_id": str(operation_id), "result_id": str(result_id)},
        )
        raise AppError("Commercial operation result archive failed", status_code=500) from exc


@router.post(
    "/{operation_id}/monitoring-observations",
    response_model=CommercialOperationMonitoringObservationResponse,
    status_code=201,
)
async def create_commercial_operation_monitoring_observation(
    operation_id: UUID,
    request: CommercialOperationMonitoringObservationCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMonitoringObservationResponse:
    """Create an operator-reviewed monitoring observation from an approved commercial result."""

    try:
        observation = await CommercialOperationService(session).create_monitoring_observation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            created_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationMonitoringObservationResponse.from_model(observation)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation monitoring observation create API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation monitoring observation create failed", status_code=500) from exc


@router.get("/{operation_id}/monitoring-observations", response_model=CommercialOperationMonitoringObservationListResponse)
async def list_commercial_operation_monitoring_observations(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / archived"),
    result_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMonitoringObservationListResponse:
    """List operator-reviewed monitoring observations for a commercial operation."""

    try:
        observations = await CommercialOperationService(session).list_monitoring_observations(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            result_id=result_id,
            limit=limit,
        )
        return CommercialOperationMonitoringObservationListResponse(
            operation_id=operation_id,
            items=[CommercialOperationMonitoringObservationResponse.from_model(item) for item in observations],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation monitoring observation list API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation monitoring observation list failed", status_code=500) from exc


@router.patch(
    "/{operation_id}/monitoring-observations/{observation_id}",
    response_model=CommercialOperationMonitoringObservationResponse,
)
async def update_commercial_operation_monitoring_observation(
    operation_id: UUID,
    observation_id: UUID,
    request: CommercialOperationMonitoringObservationUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMonitoringObservationResponse:
    """Patch a draft or rejected commercial monitoring observation."""

    try:
        observation = await CommercialOperationService(session).update_monitoring_observation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            observation_id=observation_id,
            updated_by=context.user_id,
            patch=request.model_dump(exclude_unset=True),
        )
        return CommercialOperationMonitoringObservationResponse.from_model(observation)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation monitoring observation update API failed",
            extra={"operation_id": str(operation_id), "observation_id": str(observation_id)},
        )
        raise AppError("Commercial operation monitoring observation update failed", status_code=500) from exc


@router.post(
    "/{operation_id}/monitoring-observations/{observation_id}/ready",
    response_model=CommercialOperationMonitoringObservationResponse,
)
async def ready_commercial_operation_monitoring_observation(
    operation_id: UUID,
    observation_id: UUID,
    request: CommercialOperationMonitoringObservationDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMonitoringObservationResponse:
    """Mark a commercial monitoring observation ready for review."""

    try:
        observation = await CommercialOperationService(session).mark_monitoring_observation_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            observation_id=observation_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationMonitoringObservationResponse.from_model(observation)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation monitoring observation ready API failed",
            extra={"operation_id": str(operation_id), "observation_id": str(observation_id)},
        )
        raise AppError("Commercial operation monitoring observation ready failed", status_code=500) from exc


@router.post(
    "/{operation_id}/monitoring-observations/{observation_id}/approve",
    response_model=CommercialOperationMonitoringObservationResponse,
)
async def approve_commercial_operation_monitoring_observation(
    operation_id: UUID,
    observation_id: UUID,
    request: CommercialOperationMonitoringObservationDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMonitoringObservationResponse:
    """Approve a reviewed commercial monitoring observation."""

    try:
        observation = await CommercialOperationService(session).approve_monitoring_observation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            observation_id=observation_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationMonitoringObservationResponse.from_model(observation)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation monitoring observation approve API failed",
            extra={"operation_id": str(operation_id), "observation_id": str(observation_id)},
        )
        raise AppError("Commercial operation monitoring observation approve failed", status_code=500) from exc


@router.post(
    "/{operation_id}/monitoring-observations/{observation_id}/reject",
    response_model=CommercialOperationMonitoringObservationResponse,
)
async def reject_commercial_operation_monitoring_observation(
    operation_id: UUID,
    observation_id: UUID,
    request: CommercialOperationMonitoringObservationDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMonitoringObservationResponse:
    """Reject a reviewed commercial monitoring observation for revision."""

    try:
        observation = await CommercialOperationService(session).reject_monitoring_observation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            observation_id=observation_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationMonitoringObservationResponse.from_model(observation)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation monitoring observation reject API failed",
            extra={"operation_id": str(operation_id), "observation_id": str(observation_id)},
        )
        raise AppError("Commercial operation monitoring observation reject failed", status_code=500) from exc


@router.post(
    "/{operation_id}/monitoring-observations/{observation_id}/archive",
    response_model=CommercialOperationMonitoringObservationResponse,
)
async def archive_commercial_operation_monitoring_observation(
    operation_id: UUID,
    observation_id: UUID,
    request: CommercialOperationMonitoringObservationDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMonitoringObservationResponse:
    """Archive a commercial monitoring observation while preserving the audit trail."""

    try:
        observation = await CommercialOperationService(session).archive_monitoring_observation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            observation_id=observation_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationMonitoringObservationResponse.from_model(observation)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation monitoring observation archive API failed",
            extra={"operation_id": str(operation_id), "observation_id": str(observation_id)},
        )
        raise AppError("Commercial operation monitoring observation archive failed", status_code=500) from exc


@router.post(
    "/{operation_id}/optimization-decisions",
    response_model=CommercialOperationOptimizationDecisionResponse,
    status_code=201,
)
async def create_commercial_operation_optimization_decision(
    operation_id: UUID,
    request: CommercialOperationOptimizationDecisionCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationOptimizationDecisionResponse:
    """Create an operator-reviewed optimization decision from an approved monitoring observation."""

    try:
        decision = await CommercialOperationService(session).create_optimization_decision(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            created_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationOptimizationDecisionResponse.from_model(decision)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation optimization decision create API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation optimization decision create failed", status_code=500) from exc


@router.get("/{operation_id}/optimization-decisions", response_model=CommercialOperationOptimizationDecisionListResponse)
async def list_commercial_operation_optimization_decisions(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / archived"),
    observation_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationOptimizationDecisionListResponse:
    """List operator-reviewed optimization decisions for a commercial operation."""

    try:
        decisions = await CommercialOperationService(session).list_optimization_decisions(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            observation_id=observation_id,
            limit=limit,
        )
        return CommercialOperationOptimizationDecisionListResponse(
            operation_id=operation_id,
            items=[CommercialOperationOptimizationDecisionResponse.from_model(item) for item in decisions],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation optimization decision list API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation optimization decision list failed", status_code=500) from exc


@router.patch(
    "/{operation_id}/optimization-decisions/{optimization_decision_id}",
    response_model=CommercialOperationOptimizationDecisionResponse,
)
async def update_commercial_operation_optimization_decision(
    operation_id: UUID,
    optimization_decision_id: UUID,
    request: CommercialOperationOptimizationDecisionUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationOptimizationDecisionResponse:
    """Patch a draft or rejected commercial optimization decision."""

    try:
        decision = await CommercialOperationService(session).update_optimization_decision(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            decision_id=optimization_decision_id,
            updated_by=context.user_id,
            patch=request.model_dump(exclude_unset=True),
        )
        return CommercialOperationOptimizationDecisionResponse.from_model(decision)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation optimization decision update API failed",
            extra={"operation_id": str(operation_id), "optimization_decision_id": str(optimization_decision_id)},
        )
        raise AppError("Commercial operation optimization decision update failed", status_code=500) from exc


@router.post(
    "/{operation_id}/optimization-decisions/{optimization_decision_id}/ready",
    response_model=CommercialOperationOptimizationDecisionResponse,
)
async def ready_commercial_operation_optimization_decision(
    operation_id: UUID,
    optimization_decision_id: UUID,
    request: CommercialOperationOptimizationDecisionDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationOptimizationDecisionResponse:
    """Mark a commercial optimization decision ready for review."""

    try:
        decision = await CommercialOperationService(session).mark_optimization_decision_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            decision_id=optimization_decision_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationOptimizationDecisionResponse.from_model(decision)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation optimization decision ready API failed",
            extra={"operation_id": str(operation_id), "optimization_decision_id": str(optimization_decision_id)},
        )
        raise AppError("Commercial operation optimization decision ready failed", status_code=500) from exc


@router.post(
    "/{operation_id}/optimization-decisions/{optimization_decision_id}/approve",
    response_model=CommercialOperationOptimizationDecisionResponse,
)
async def approve_commercial_operation_optimization_decision(
    operation_id: UUID,
    optimization_decision_id: UUID,
    request: CommercialOperationOptimizationDecisionDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationOptimizationDecisionResponse:
    """Approve a reviewed commercial optimization decision."""

    try:
        decision = await CommercialOperationService(session).approve_optimization_decision(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            decision_id=optimization_decision_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationOptimizationDecisionResponse.from_model(decision)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation optimization decision approve API failed",
            extra={"operation_id": str(operation_id), "optimization_decision_id": str(optimization_decision_id)},
        )
        raise AppError("Commercial operation optimization decision approve failed", status_code=500) from exc


@router.post(
    "/{operation_id}/optimization-decisions/{optimization_decision_id}/reject",
    response_model=CommercialOperationOptimizationDecisionResponse,
)
async def reject_commercial_operation_optimization_decision(
    operation_id: UUID,
    optimization_decision_id: UUID,
    request: CommercialOperationOptimizationDecisionDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationOptimizationDecisionResponse:
    """Reject a reviewed commercial optimization decision for revision."""

    try:
        decision = await CommercialOperationService(session).reject_optimization_decision(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            decision_id=optimization_decision_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationOptimizationDecisionResponse.from_model(decision)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation optimization decision reject API failed",
            extra={"operation_id": str(operation_id), "optimization_decision_id": str(optimization_decision_id)},
        )
        raise AppError("Commercial operation optimization decision reject failed", status_code=500) from exc


@router.post(
    "/{operation_id}/optimization-decisions/{optimization_decision_id}/archive",
    response_model=CommercialOperationOptimizationDecisionResponse,
)
async def archive_commercial_operation_optimization_decision(
    operation_id: UUID,
    optimization_decision_id: UUID,
    request: CommercialOperationOptimizationDecisionDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationOptimizationDecisionResponse:
    """Archive a commercial optimization decision while preserving the audit trail."""

    try:
        decision = await CommercialOperationService(session).archive_optimization_decision(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            decision_id=optimization_decision_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationOptimizationDecisionResponse.from_model(decision)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation optimization decision archive API failed",
            extra={"operation_id": str(operation_id), "optimization_decision_id": str(optimization_decision_id)},
        )
        raise AppError("Commercial operation optimization decision archive failed", status_code=500) from exc


@router.post("/{operation_id}/links", response_model=CommercialOperationLinkResponse, status_code=201)
async def create_commercial_operation_link(
    operation_id: UUID,
    request: CommercialOperationLinkCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationLinkResponse:
    """Attach evidence, handoff, or runtime context to a commercial operation."""

    try:
        link = await CommercialOperationService(session).create_link(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            **request.model_dump(),
        )
        return CommercialOperationLinkResponse.from_model(link)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception("Commercial operation link create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation link create failed", status_code=500) from exc


@router.get("/{operation_id}/links", response_model=CommercialOperationLinkListResponse)
async def list_commercial_operation_links(
    operation_id: UUID,
    link_type: str | None = Query(default=None, description="conversation / artifact / task_run / workflow_run / rag_document / knowledge_source / approval / external"),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationLinkListResponse:
    """List evidence and handoff links for a commercial operation."""

    try:
        links = await CommercialOperationService(session).list_links(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            link_type=link_type,
            limit=limit,
        )
        return CommercialOperationLinkListResponse(
            operation_id=operation_id,
            items=[CommercialOperationLinkResponse.from_model(link) for link in links],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation link list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation link list failed", status_code=500) from exc


@router.delete("/{operation_id}/links/{link_id}", response_model=CommercialOperationLinkResponse)
async def delete_commercial_operation_link(
    operation_id: UUID,
    link_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationLinkResponse:
    """Remove one commercial operation evidence or handoff link."""

    try:
        link = await CommercialOperationService(session).delete_link(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            link_id=link_id,
        )
        return CommercialOperationLinkResponse.from_model(link)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation link delete API failed",
            extra={"operation_id": str(operation_id), "link_id": str(link_id)},
        )
        raise AppError("Commercial operation link delete failed", status_code=500) from exc
