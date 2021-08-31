from patterns.detect.find_self_assignment import CheckForSelfAssignment, CheckForSelfDoubleAssignment
from patterns.detect.find_float_equality import FloatEqualityDetector
from patterns.detect.dont_use_enum import DontUseEnumDetector
from patterns.detect.inheritance_unsafe_get_resource import GetResourceDetector
from patterns.detect.incompat_mask import IncompatMaskDetector
from patterns.detect.serializable_idiom import DefSerialVersionID, DefReadResolveMethod, DefPrivateMethod
from patterns.detect.find_self_comparison import CheckForSelfComputation, CheckForSelfComparison
from patterns.detect.dont_catch_illegal_monitor_state_exception import DontCatchIllegalMonitorStateException
from patterns.detect.find_rough_constants import FindRoughConstantsDetector
from patterns.detect.naming import SimpleSuperclassNameDetector, SimpleInterfaceNameDetector, HashCodeNameDetector, ToStringNameDetector, EqualNameDetector, ClassNameConventionDetector, MethodNameConventionDetector
from patterns.detect.method_return_check import NotThrowDetector
from patterns.detect.find_dead_local_stores import FindDeadLocalIncrementInReturn
from patterns.detect.overriding_equals_not_symmetrical import EqualsClassNameDetector
from patterns.detect.questionable_boolean_assignment import BooleanAssignmentDetector
from patterns.detect.format_string_checker import NewLineDetector
from patterns.detect.find_finalize_invocations import ExplicitInvDetector, PublicAccessDetector
from patterns.detect.bad_syntax_for_regular_expression import SingleDotPatternDetector, FileSeparatorAsRegexpDetector
from patterns.detect.find_ref_comparison import EqualityDetector, CallToNullDetector
from patterns.detect.static_calendar_detector import StaticDateFormatDetector
from patterns.detect.infinite_recursive_loop import CollectionAddItselfDetector
from patterns.detect.find_puzzlers import BadMonthDetector, ShiftAddPriorityDetector, OverwrittenIncrementDetector
from patterns.detect.find_bad_cast import FindBadCastDetector
from patterns.detect.find_unrelated_types_in_generic_container import SuspiciousCollectionMethodDetector
from patterns.detect.dumb_methods import FinalizerOnExitDetector, RandomOnceDetector, RandomD2IDetector, StringCtorDetector, InvalidMinMaxDetector

DETECTOR_DICT = {
    "CheckForSelfAssignment": CheckForSelfAssignment,
    "CheckForSelfDoubleAssignment": CheckForSelfDoubleAssignment,
    "FloatEqualityDetector": FloatEqualityDetector,
    "DontUseEnumDetector": DontUseEnumDetector,
    "GetResourceDetector": GetResourceDetector,
    "IncompatMaskDetector": IncompatMaskDetector,
    "DefSerialVersionID": DefSerialVersionID,
    "DefReadResolveMethod": DefReadResolveMethod,
    "DefPrivateMethod": DefPrivateMethod,
    "CheckForSelfComputation": CheckForSelfComputation,
    "CheckForSelfComparison": CheckForSelfComparison,
    "DontCatchIllegalMonitorStateException": DontCatchIllegalMonitorStateException,
    "FindRoughConstantsDetector": FindRoughConstantsDetector,
    "SimpleSuperclassNameDetector": SimpleSuperclassNameDetector,
    "SimpleInterfaceNameDetector": SimpleInterfaceNameDetector,
    "HashCodeNameDetector": HashCodeNameDetector,
    "ToStringNameDetector": ToStringNameDetector,
    "EqualNameDetector": EqualNameDetector,
    "ClassNameConventionDetector": ClassNameConventionDetector,
    "MethodNameConventionDetector": MethodNameConventionDetector,
    "NotThrowDetector": NotThrowDetector,
    "FindDeadLocalIncrementInReturn": FindDeadLocalIncrementInReturn,
    "EqualsClassNameDetector": EqualsClassNameDetector,
    "BooleanAssignmentDetector": BooleanAssignmentDetector,
    "NewLineDetector": NewLineDetector,
    "ExplicitInvDetector": ExplicitInvDetector,
    "PublicAccessDetector": PublicAccessDetector,
    "SingleDotPatternDetector": SingleDotPatternDetector,
    "FileSeparatorAsRegexpDetector": FileSeparatorAsRegexpDetector,
    "EqualityDetector": EqualityDetector,
    "CallToNullDetector": CallToNullDetector,
    "StaticDateFormatDetector": StaticDateFormatDetector,
    "CollectionAddItselfDetector": CollectionAddItselfDetector,
    "BadMonthDetector": BadMonthDetector,
    "ShiftAddPriorityDetector": ShiftAddPriorityDetector,
    "OverwrittenIncrementDetector": OverwrittenIncrementDetector,
    "FindBadCastDetector": FindBadCastDetector,
    "SuspiciousCollectionMethodDetector": SuspiciousCollectionMethodDetector,
    "FinalizerOnExitDetector": FinalizerOnExitDetector,
    "RandomOnceDetector": RandomOnceDetector,
    "RandomD2IDetector": RandomD2IDetector,
    "StringCtorDetector": StringCtorDetector,
    "InvalidMinMaxDetector": InvalidMinMaxDetector
}