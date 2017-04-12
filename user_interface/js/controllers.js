/*
 * Calaca - Search UI for Elasticsearch
 * https://github.com/romansanchez/Calaca
 * http://romansanchez.me
 * @rooomansanchez
 *
 * v1.2.0
 * MIT License
 */

/* Calaca Controller
 *
 * On change in search box, search() will be called, and results are bind to scope as results[]
 *
 */
Calaca.controller('calacaCtrl', ['calacaService', '$scope', '$location', function (results, $scope, $location) {

        //Init empty array
        $scope.results = [];

        //Init offset
        $scope.offset = 0;

        var paginationTriggered;
        var maxResultsSize = CALACA_CONFIGS.size;
        var searchTimeout;

        $scope.delayedSearch = function (mode) {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function () {
                $scope.search(mode)
            }, CALACA_CONFIGS.search_delay);
        }

        //On search, reinitialize array, then perform search and load results
        $scope.search = function (m) {
            $scope.results = [];
            $scope.offset = m == 0 ? 0 : $scope.offset;//Clear offset if new query
            $scope.loading = m == 0 ? false : true;//Reset loading flag if new query

            if (m == -1 && paginationTriggered) {
                if ($scope.offset - maxResultsSize >= 0) $scope.offset -= maxResultsSize;
            }
            if (m == 1 && paginationTriggered) {
                $scope.offset += maxResultsSize;
            }
            $scope.paginationLowerBound = $scope.offset + 1;
            $scope.paginationUpperBound = ($scope.offset == 0) ? maxResultsSize : $scope.offset + maxResultsSize;

            $

            $scope.loadResults(m);

        };

        function toTitleCase(str) {
            return str.replace(/\w\S*/g, function (txt) {
                return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
            });
        }

        var toType = function (obj) {
            return ({}).toString.call(obj).match(/\s([a-zA-Z]+)/)[1].toLowerCase()
        }

        //Load search results into array
        $scope.loadResults = function (m) {
            results.search($scope.query, m, $scope.offset).then(function (a) {

                //Load results
                var i = 0;
                for (; i < a.hits.length; i++) {

                    // check the type of the element, to apply different styling
                    if (a.hits[i]._type == 'hospital') {

                        a.hits[i].location.address = a.hits[i].location.address.join(", ");
                        a.hits[i].totalCount = 0;
                        for (trail in a.hits[i].clinicaltrials) {

                            a.hits[i].clinicaltrials[trail].conditions = a.hits[i].clinicaltrials[trail].conditions.join(", ");
                            var n = a.hits[i].clinicaltrials[trail].conditions.indexOf(toTitleCase($scope.query));

                            if (n == -1) {
                                a.hits[i].clinicaltrials[trail].conditions = n;
                            } else {
                                a.hits[i].clinicaltrials[trail].matches = true;
                                a.hits[i].totalCount += 1;
                            }

                            if (a.hits[i].clinicaltrials[trail].condition_mesh != null) {
                                console.log(a.hits[i].clinicaltrials[trail].condition_mesh);
                                a.hits[i].clinicaltrials[trail].condition_mesh = a.hits[i].clinicaltrials[trail].condition_mesh.join(", ");

                            }
                            if (a.hits[i].clinicaltrials[trail].keywords != null) {
                                a.hits[i].clinicaltrials[trail].keywords = a.hits[i].clinicaltrials[trail].keywords.join(", ");
                            }

                        }
                        a.hits[i].isHospital = true;

                        // Check if contact info exists
                        if (a.hits[i].contact.phone != null || a.hits[i].contact.twitter != null || a.hits[i].contact.facebook != null) {
                            a.hits[i].contactExists = true;
                        }

                    }

                    $scope.results.push(a.hits[i]);
                }

                //Set time took
                $scope.timeTook = a.timeTook;

                //Set total number of hits that matched query
                $scope.hits = a.hitsCount;

                //Pluralization
                $scope.resultsLabel = ($scope.hits != 1) ? "results" : "result";

                //Check if pagination is triggered
                paginationTriggered = $scope.hits > maxResultsSize ? true : false;

                //Set loading flag if pagination has been triggered
                if (paginationTriggered) {
                    $scope.loading = true;
                }
            });
        };

        $scope.paginationEnabled = function () {
            return paginationTriggered ? true : false;
        };


    }]
);