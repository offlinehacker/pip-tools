import sys

from .log import logger
from .datastructures import SpecSet, Spec


def print_specset(specset, round, debug=False):
    (logger.debug if debug else logger.info)('After round #%s:' % (round,))
    for spec in sorted(specset, key=lambda s: s.description()):
        (logger.debug if debug else logger.info)(
            '  - %s' % (spec.description(),))


class DependencyResolver(object):
    def __init__(self, spec_set, package_manager):
        """This class resolves a given SpecSet by querying the given
        PackageManager.
        """
        self.spec_set = spec_set
        self.pkgmgr = package_manager

    def resolve_one_round(self):
        """Resolves one level of the current spec set, by finding best matches
        for the current spec set in the package manager and returning all
        (new) requirements for those packages.

        Returns whether the spec set was changed significantly by this round.
        """

        new_deps = self.find_new_dependencies()
        self.spec_set.add_specs(new_deps)
        return len(new_deps) > 0

    def resolve(self, max_rounds=12):
        """Resolves the spec set one round at a time, until the set does not
        change significantly anymore.  Protects against infinite loops by
        breaking out after a max number rounds.
        """

        round = 0
        while True:
            round += 1
            if round > max_rounds:
                raise RuntimeError('Spec set was not resolved after %d rounds. '
                        'This is likely a bug.' % max_rounds)

            if not self.resolve_one_round():
                # Break as soon as nothing significant is added in this round
                print_specset(self.spec_set, round)
                break

            print_specset(self.spec_set, round, debug=True)

        # Return the pinned spec set
        return self.pin_spec_set()

    def pin_spec_set(self):
        """Pins all packages in given resolved spec set and returns a new spec
        set.  Requires the input spec set to be resolved.
        """
        new_spec_set = SpecSet()
        for spec in self.spec_set.normalize():
            best_version = self.pkgmgr.find_best_match(spec)
            spec.pinned = best_version
            new_spec_set.add_spec(spec)
        return new_spec_set

    def find_all_dependencies(self):
        """Finds best matches for the current spec set in the package manager,
        returning all requirements for those packages.
        """
        spec_set = self.spec_set
        pkgmgr = self.pkgmgr

        deps = set()
        for spec in spec_set.normalize():
            version = pkgmgr.find_best_match(spec)
            pkg_deps = pkgmgr.get_dependencies(spec.name, version, spec.extra)

            # Append source information to the new specs
            if spec.source:
                source = '%s ~> %s' % (spec.source, spec)
            else:
                source = '%s' % spec

            for d, _ in pkg_deps:
                deps.update([d.add_source(source)])

        return deps

    def find_new_dependencies(self):
        """Finds all dependencies for the given spec set (in the package
        manager), but only returns what specs are new to the set.
        """
        all_deps = self.find_all_dependencies()
        return all_deps - set(self.spec_set)  # only return _new_ specs
